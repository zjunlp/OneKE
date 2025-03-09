from models import *
from utils import *
from .extraction_agent import ExtractionAgent
from .knowledge_base.case_repository import CaseRepositoryHandler
class ReflectionGenerator:
    def __init__(self, llm: BaseEngine):
        self.llm = llm

    def get_reflection(self, instruction="", examples="", text="",schema="", result=""):
        result = json.dumps(result)
        examples = bad_case_wrapper(examples)
        prompt = reflect_instruction.format(instruction=instruction, examples=examples, text=text, schema=schema, result=result)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        return response

class ReflectionAgent:
    def __init__(self, llm: BaseEngine, case_repo: CaseRepositoryHandler):
        self.llm = llm
        self.module = ReflectionGenerator(llm = llm)
        self.extractor = ExtractionAgent(llm = llm, case_repo = case_repo)
        self.case_repo = case_repo
        self.methods = ["reflect_with_case"]

    def __select_result(self, result_list):
        dict_objects = [obj for obj in result_list if isinstance(obj, dict)]
        if dict_objects:
            selected_obj = max(dict_objects, key=lambda d: len(json.dumps(d)))
        else:
            selected_obj = max(result_list, key=lambda o: len(json.dumps(o)))
        return selected_obj

    def __self_consistance_check(self, data: DataPoint):
        extract_func = list(data.result_trajectory.keys())[-1]
        if hasattr(self.extractor, extract_func):
            result_trails = []
            result_trails.append(data.result_list)
            extract_func = getattr(self.extractor, extract_func)
            temperature = [0.5, 1]
            for index in range(2):
                self.module.llm.set_hyperparameter(temperature=temperature[index])
                data = extract_func(data)
                result_trails.append(data.result_list)
            self.module.llm.set_hyperparameter()
            consistant_result = []
            reflect_index = []
            for index, elements in enumerate(zip(*result_trails)):
                normalized_elements = [normalize_obj(e) for e in elements]
                element_counts = Counter(normalized_elements)
                selected_element = next((elements[i] for i, element in enumerate(normalized_elements)
                                        if element_counts[element] >= 2), None)
                if selected_element is None:
                    selected_element = self.__select_result(elements)
                    reflect_index.append(index)
                consistant_result.append(selected_element)
            data.set_result_list(consistant_result)
            return reflect_index

    def reflect_with_case(self, data: DataPoint):
        if data.result_list == []:
            return data
        reflect_index = self.__self_consistance_check(data)
        reflected_result_list = data.result_list
        for idx in reflect_index:
            text = data.chunk_text_list[idx]
            result = data.result_list[idx]
            examples = json.dumps(self.case_repo.query_bad_case(data))
            reflected_res = self.module.get_reflection(instruction=data.instruction, examples=examples, text=text, schema=data.output_schema, result=result)
            reflected_result_list[idx] = reflected_res
        data.set_result_list(reflected_result_list)
        function_name = current_function_name()
        data.update_trajectory(function_name, data.result_list)
        return data
