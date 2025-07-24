from typing import Literal
from models import *
from utils import *
from modules import *
from construct import *

class Pipeline:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.llm = llm
        self.case_repo = CaseRepositoryHandler(llm = llm)
        self.schema_agent = SchemaAgent(llm = llm)
        self.extraction_agent = ExtractionAgent(llm = llm, case_repo = self.case_repo)
        self.reflection_agent = ReflectionAgent(llm = llm, case_repo = self.case_repo)

    def __check_consistancy(self, llm, task, mode, update_case):
        if llm.name == "OneKE":
            if task == "Base" or task == "Triple":
                raise ValueError("The finetuned OneKE only supports quick extraction mode for NER, RE and EE Task.")
            else:
                mode = "quick"
                update_case = False
                print("The fine-tuned OneKE defaults to quick extraction mode without case update.")
                return mode, update_case
        return mode, update_case

    def __init_method(self, data: DataPoint, method):
        default_order = ["schema_agent", "extraction_agent", "reflection_agent"]
        
        # Ensure method is a dictionary
        if not isinstance(method, dict):
            method = {"extraction_agent": "extract_information_direct"}
        
        if "schema_agent" not in method:
            method["schema_agent"] = "get_default_schema"
        if data.task != "Base":
            method["schema_agent"] = "get_retrieved_schema"
        if "extraction_agent" not in method:
            method["extraction_agent"] = "extract_information_direct"
        sorted_process_method = {key: method[key] for key in default_order if key in method}
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
        elif data.task == "Triple":
            data.instruction = config['agent']['default_triple']
            data.output_schema = "TripleList"
        return data

    # main entry
    def get_extract_result(self,
                           task: TaskType,
                           three_agents = {},
                           construct = {},
                           instruction: str = "",
                           text: str = "",
                           output_schema: str = "",
                           constraint: str = "",
                           use_file: bool = False,
                           file_path: str = "",
                           truth: str = "",
                           mode: str = "quick",
                           update_case: bool = False,
                           show_trajectory: bool = False,
                           isgui: bool = False,
                           iskg: bool = False,
                           config_name: str = "", 
                           ):

        # Check Consistancy
        mode, update_case = self.__check_consistancy(self.llm, task, mode, update_case)

        # Load Data
        data = DataPoint(task=task, instruction=instruction, text=text, output_schema=output_schema, constraint=constraint, use_file=use_file, file_path=file_path, truth=truth)
        data = self.__init_data(data)
        if mode in config['agent']['mode'].keys():
            process_method = config['agent']['mode'][mode].copy()
        else:
            process_method = mode

        if isgui and mode == "customized":
            process_method = three_agents
            print("Customized 3-Agents: ", three_agents)

        sorted_process_method = self.__init_method(data, process_method)
        print("Process Method: ", sorted_process_method)

        print_schema = False #
        frontend_schema = "" #
        frontend_res = "" #

        # Information Extract
        for agent_name, method_name in sorted_process_method.items():
            agent = getattr(self, agent_name, None)
            if not agent:
                continue
            method = getattr(agent, method_name, None)
            if not method:
                continue
            data = method(data)
            if not print_schema and data.print_schema: #
                print("Schema: \n", data.print_schema)
                frontend_schema = data.print_schema
                print_schema = True
        # Only call summarize_answer if extraction_agent is available
        if self.extraction_agent is not None:
            data = self.extraction_agent.summarize_answer(data)
        else:
            # If no extraction agent, set an empty result based on task type
            if data.task == "NER":
                data.pred = []
            elif data.task == "RE":
                data.pred = []
            elif data.task == "EE":
                data.pred = []
            elif data.task == "Triple":
                data.pred = []
            else:
                data.pred = []

        # show result
        if not isgui:
            if show_trajectory:
                print("Extraction Trajectory: \n", json.dumps(data.get_result_trajectory(), indent=4, ensure_ascii=False))
            
            # Console output in formatted JSON
            if type(data.pred) is not str:
                extraction_result = json.dumps(data.pred, indent=4, ensure_ascii=False)
            print("Extraction Result: \n", extraction_result)
            
            # Add download functionality
            if config_name:
                import os
                # Create result directory
                result_dir = "examples/results"
                if not os.path.exists(result_dir):
                    os.makedirs(result_dir)
                
                # Extract filename from full path (remove path and extension)
                base_name = os.path.splitext(os.path.basename(config_name))[0]
                
                # Save extraction result as formatted JSON
                result_file_path = os.path.join(result_dir, f"{base_name}.json")
                with open(result_file_path, 'w', encoding='utf-8') as f:
                    f.write(extraction_result)
                print(f"Extraction Result has been saved to: {result_file_path}")

        # construct KG
        if iskg:
            myurl = construct['url']
            myusername = construct['username']
            mypassword = construct['password']
            print(f"Construct KG in your {construct['database']} now...")
            cypher_statements = generate_cypher_statements(extraction_result)
            execute_cypher_statements(uri=myurl, user=myusername, password=mypassword, cypher_statements=cypher_statements)

        frontend_res = data.pred

        # Case Update
        if update_case:
            if self.case_repo is None:
                print("Warning: Case update not available - CaseRepositoryHandler not loaded.")
            else:
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

        return result, trajectory, frontend_schema, frontend_res
