from models import *
from utils import *
from .knowledge_base.case_repository import CaseRepositoryHandler

class InformationExtractor:
    def __init__(self, llm: BaseEngine):
        self.llm = llm    
    
    def extract_information(self, instruction="", text="", examples="", schema="", additional_info=""):
        examples = example_wrapper(examples)
        prompt = extract_instruction.format(instruction=instruction, examples=examples, text=text, additional_info=additional_info, schema=schema)
        response = self.llm.get_chat_response(prompt) 
        print("======================Prompt===================\n", prompt)
        print("======================Response===================\n", response)
        response = extract_json_dict(response)
        return response

    def summarize_answer(self, instruction="", answer_list="", schema="", additional_info=""):
        prompt = summarize_instruction.format(instruction=instruction, answer_list=answer_list, schema=schema, additional_info=additional_info)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        return response
    
class ExtractionAgent:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.module = InformationExtractor(llm = llm)
        self.case_repo = CaseRepositoryHandler(llm = llm)
        self.methods = ["extract_information_direct", "extract_information_with_case"]

    def __get_constraint(self, data: DataPoint):
        if data.constraint == "":
            return data
        if data.task == "NER":
            constraint = json.dumps(data.constraint)
            data.constraint = f"\n**Entity Type Constraint**: The type of entities must be chosen from the following list.\n{constraint}\n"
        elif data.task == "RE":
            constraint = json.dumps(data.constraint)
            data.constraint = f"\n**Relation Type Constraint**: The type of relations must be chosen from the following list.\n{constraint}\n"
        elif data.task == "EE":
            constraint = json.dumps(data.constraint)
            data.constraint = f"\n**Event Extraction Constraint**: The event type must be chosen from 'event_type' in the following list, and the corresponding arguments should be extracted based on the keys defined in 'arguments'. \n{constraint}\n"
        return data
            
    def extract_information_direct(self, data: DataPoint):
        data = self.__get_constraint(data)
        result_list = []
        for chunk_text in data.chunk_text_list:
            extract_direct_result = self.module.extract_information(instruction=data.instruction, text=chunk_text, schema=data.output_schema, examples="", additional_info=data.constraint)
            result_list.append(extract_direct_result)
        function_name = current_function_name()
        data.set_result_list(result_list)
        data.update_trajectory(function_name, result_list)
        return data
    
    def extract_information_with_case(self, data: DataPoint):
        data = self.__get_constraint(data)
        result_list = []
        for chunk_text in data.chunk_text_list:
            examples = self.case_repo.query_good_case(data)
            extract_case_result = self.module.extract_information(instruction=data.instruction, text=chunk_text, schema=data.output_schema, examples=examples, additional_info=data.constraint)
            result_list.append(extract_case_result)
        function_name = current_function_name()
        data.set_result_list(result_list)
        data.update_trajectory(function_name, result_list)
        return data
    
    def summarize_answer(self, data: DataPoint):
        if len(data.result_list) == 0:
            return data
        if len(data.result_list) == 1:
            data.set_pred(data.result_list[0])
            return data
        summarized_result = self.module.summarize_answer(instruction=data.instruction, answer_list=data.result_list, schema=data.output_schema, additional_info=data.constraint)
        funtion_name = current_function_name()
        data.set_pred(summarized_result)
        data.update_trajectory(funtion_name, summarized_result)
        return data