from models import *
from utils import *
from .knowledge_base.case_repository import CaseRepositoryHandler

class InformationExtractor:
    def __init__(self, llm: BaseEngine):
        self.llm = llm

    def extract_information(self, instruction="", text="", examples="", schema="", additional_info=""):
        examples = good_case_wrapper(examples)
        prompt = extract_instruction.format(instruction=instruction, examples=examples, text=text, additional_info=additional_info, schema=schema)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        return response

    def extract_information_compatible(self, task="", text="", constraint=""):
        instruction = instruction_mapper.get(task)
        prompt = extract_instruction_json.format(instruction=instruction, constraint=constraint, input=text)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        return response

    def summarize_answer(self, instruction="", answer_list="", schema="", additional_info=""):
        prompt = summarize_instruction.format(instruction=instruction, answer_list=answer_list, schema=schema, additional_info=additional_info)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        return response

class ExtractionAgent:
    def __init__(self, llm: BaseEngine, case_repo: CaseRepositoryHandler):
        self.llm = llm
        self.module = InformationExtractor(llm = llm)
        self.case_repo = case_repo
        self.methods = ["extract_information_direct", "extract_information_with_case"]

    def __get_constraint(self, data: DataPoint):
        if data.constraint == "":
            return data
        if data.task == "NER":
            constraint = json.dumps(data.constraint)
            if "**Entity Type Constraint**" in constraint or self.llm.name == "OneKE":
                return data
            data.constraint = f"\n**Entity Type Constraint**: The type of entities must be chosen from the following list.\n{constraint}\n"
        elif data.task == "RE":
            constraint = json.dumps(data.constraint)
            if "**Relation Type Constraint**" in constraint or self.llm.name == "OneKE":
                return data
            data.constraint = f"\n**Relation Type Constraint**: The type of relations must be chosen from the following list.\n{constraint}\n"
        elif data.task == "EE":
            constraint = json.dumps(data.constraint)
            if "**Event Extraction Constraint**" in constraint:
                return data
            if self.llm.name != "OneKE":
                data.constraint = f"\n**Event Extraction Constraint**: The event type must be selected from the following dictionary keys, and its event arguments should be chosen from its corresponding dictionary values. \n{constraint}\n"
            else:
                try:
                    result = [
                                {
                                    "event_type": key,
                                    "trigger": True,
                                    "arguments": value
                                }
                                for key, value in data.constraint.items()
                            ]
                    data.constraint = json.dumps(result)
                except:
                    print("Invalid Constraint: Event Extraction constraint must be a dictionary with event types as keys and lists of arguments as values.", data.constraint)
        elif data.task == "Triple":
            constraint = json.dumps(data.constraint)
            if "**Triple Extraction Constraint**" in constraint:
                return data
            if self.llm.name != "OneKE":
                if len(data.constraint) == 1: # 1 list means entity
                    data.constraint = f"\n**Triple Extraction Constraint**: Entities type must chosen from following list:\n{constraint}\n"
                elif len(data.constraint) == 2: # 2 list means entity and relation
                    if data.constraint[0] == []:
                        data.constraint = f"\n**Triple Extraction Constraint**: Relation type must chosen from following list:\n{data.constraint[1]}\n"
                    elif data.constraint[1] == []:
                        data.constraint = f"\n**Triple Extraction Constraint**: Entities type must chosen from following list:\n{data.constraint[0]}\n"
                    else:
                        data.constraint = f"\n**Triple Extraction Constraint**: Entities type must chosen from following list:\n{data.constraint[0]}\nRelation type must chosen from following list:\n{data.constraint[1]}\n"
                elif len(data.constraint) == 3: # 3 list means entity, relation and object
                    if data.constraint[0] == []:
                        data.constraint = f"\n**Triple Extraction Constraint**: Relation type must chosen from following list:\n{data.constraint[1]}\nObject Entities must chosen from following list:\n{data.constraint[2]}\n"
                    elif data.constraint[1] == []:
                        data.constraint = f"\n**Triple Extraction Constraint**: Subject Entities must chosen from following list:\n{data.constraint[0]}\nObject Entities must chosen from following list:\n{data.constraint[2]}\n"
                    elif data.constraint[2] == []:
                        data.constraint = f"\n**Triple Extraction Constraint**: Subject Entities must chosen from following list:\n{data.constraint[0]}\nRelation type must chosen from following list:\n{data.constraint[1]}\n"
                    else:
                        data.constraint = f"\n**Triple Extraction Constraint**: Subject Entities must chosen from following list:\n{data.constraint[0]}\nRelation type must chosen from following list:\n{data.constraint[1]}\nObject Entities must chosen from following list:\n{data.constraint[2]}\n"
                else:
                    data.constraint = f"\n**Triple Extraction Constraint**: The type of entities must be chosen from the following list:\n{constraint}\n"
            else:
                print("OneKE does not support Triple Extraction task now, please wait for the next version.")
            # print("data.constraint", data.constraint)
        return data

    def extract_information_direct(self, data: DataPoint):
        data = self.__get_constraint(data)
        result_list = []
        for chunk_text in data.chunk_text_list:
            if self.llm.name != "OneKE":
                extract_direct_result = self.module.extract_information(instruction=data.instruction, text=chunk_text, schema=data.output_schema, examples="", additional_info=data.constraint)
            else:
                extract_direct_result = self.module.extract_information_compatible(task=data.task, text=chunk_text, constraint=data.constraint)
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