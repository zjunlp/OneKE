from typing import Literal
from models import *
from utils import *
from modules import *


class Pipeline:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.case_repo = CaseRepositoryHandler(llm = llm)
        self.schema_agent = SchemaAgent(llm = llm)
        self.extraction_agent = ExtractionAgent(llm = llm, case_repo = self.case_repo)
        self.reflection_agent = ReflectionAgent(llm = llm, case_repo = self.case_repo)

    def __check_consistancy(self, llm, task, mode, update_case):
        if llm.name == "OneKE":
            if task == "Base":
                raise ValueError("The finetuned OneKE only supports quick extraction mode for NER, RE and EE Task.")
            else:
                mode = "quick"
                update_case = False
                print("The fine-tuned OneKE defaults to quick extraction mode without case update.")
                return mode, update_case
        return mode, update_case

    def __init_method(self, data: DataPoint, process_method):
        default_order = ["schema_agent", "extraction_agent", "reflection_agent"]
        if "schema_agent" not in process_method:
            process_method["schema_agent"] = "get_default_schema"
        if data.task != "Base":
            process_method["schema_agent"] = "get_retrieved_schema"
        if "extraction_agent" not in process_method:
            process_method["extraction_agent"] = "extract_information_direct"
        sorted_process_method = {key: process_method[key] for key in default_order if key in process_method}
        return sorted_process_method

    def __init_data(self, data: DataPoint):
        if data.task == "NER":
            data.instruction = config['agent']['default_ner']
            data.output_schema = "EntityList"
        elif data.task == "RE":
            data.instruction = config['agent']['default_re']
            data.output_schema = "RelationList"
        elif data.task == "EE":
            data.instruction = config['agent']['default_ee']
            data.output_schema = "EventList"
        return data

    # main entry
    def get_extract_result(self,
                           task: TaskType,
                           instruction: str = "",
                           text: str = "",
                           output_schema: str = "",
                           constraint: str = "",
                           use_file: bool = False,
                           file_path: str = "",
                           truth: str = "",
                           mode: str = "quick",
                           update_case: bool = False,
                           show_trajectory: bool = False
                           ):

        # Check Consistancy
        mode, update_case = self.__check_consistancy(self.llm, task, mode, update_case)

        # Load Data
        data = DataPoint(task=task, instruction=instruction, text=text, output_schema=output_schema, constraint=constraint, use_file=use_file, file_path=file_path, truth=truth)
        data = self.__init_data(data)
        if mode in config['agent']['mode'].keys():
            process_method = config['agent']['mode'][mode]
        else:
            process_method = mode
        sorted_process_method = self.__init_method(data, process_method)
        print("Process Method: ", sorted_process_method)

        # Information Extract
        for agent_name, method_name in sorted_process_method.items():
            agent = getattr(self, agent_name, None)
            if not agent:
                raise AttributeError(f"{agent_name} does not exist.")
            method = getattr(agent, method_name, None)
            if not method:
                raise AttributeError(f"Method '{method_name}' not found in {agent_name}.")
            data = method(data)
        data = self.extraction_agent.summarize_answer(data)

        # show result
        if show_trajectory:
            print("Extraction Trajectory: \n", json.dumps(data.get_result_trajectory(), indent=2))
        print("Extraction Result: \n", json.dumps(data.pred, indent=2))

        # Case Update
        if update_case:
            if (data.truth == ""):
                truth = input("Please enter the correct answer you prefer, or just press Enter to accept the current answer: ")
                if truth.strip() == "":
                    data.truth = data.pred
                else:
                    data.truth = extract_json_dict(truth)
            self.case_repo.update_case(data)

        # return result
        result = data.pred
        trajectory = data.get_result_trajectory()

        return result, trajectory
