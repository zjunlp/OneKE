from typing import Literal
from models import *
from utils import *
from modules import *
import itertools

class Pipeline:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.schema_agent = SchemaAgent(llm = llm)
        self.extraction_agent = ExtractionAgent(llm = llm)
        self.reflection_agent = ReflectionAgent(llm = llm)        
        self.case_repo = CaseRepositoryHandler(llm = llm)
    
    def __init_method(self, process_method):
        default_order = ["schema_agent", "extraction_agent", "reflection_agent"]
        if "schema_agent" not in process_method:
            process_method["schema_agent"] = "get_default_schema"
        if "extraction_agent" not in process_method:
            process_method["extraction_agent"] = "extract_information_direct"
        sorted_process_method = {key: process_method[key] for key in default_order if key in process_method}
        return sorted_process_method
            
    
    # init data point
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
                           truth: str = "",
                           mode: str = "direct",
                           update_case: bool = False
                           ):
        
        data = DataPoint(task=task, instruction=instruction, text=text, output_schema=output_schema, constraint=constraint, use_file=use_file, truth=truth)
        data = self.__init_data(data)
        process_method = config['agent']['mode'][mode]
        sorted_process_method = self.__init_method(process_method)
        
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
        
        # Case Update
        if update_case:
            self.case_repo.update_case(data)
        
        # return result
        result = data.pred
        trajectory = data.get_result_trajectory()
        
        return result, trajectory