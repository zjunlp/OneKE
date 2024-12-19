from models import *
from utils import *
from .knowledge_base import schema_repository
from langchain_core.output_parsers import JsonOutputParser

class SchemaAnalyzer:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        
    def serialize_schema(self, schema) -> str:
        if isinstance(schema, (str, list, dict, set, tuple)):
            return schema    
        try:
            parser = JsonOutputParser(pydantic_object = schema)
            schema = parser.get_format_instructions()
        except:
            return schema
        return schema
        
    def redefine_text(self, text_analysis):
        try:
            field = text_analysis['field']
            genre = text_analysis['genre']
        except:
            return text_analysis    
        prompt = f"Below is a portion of the text to be extracted. This text is from the field of {field} and represents the genre of {genre}."
        return prompt
        
    def get_text_analysis(self, text: str):
        output_schema = self.serialize_schema(schema_repository.TextDescription)
        prompt = text_analysis_instruction.format(examples="", text=text, schema=output_schema)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        response = self.redefine_text(response)
        return response    
    
    def get_deduced_schema_json(self, instruction: str, text: str, distilled_text: str):
        prompt = deduced_schema_json_instruction.format(examples="", instruction=instruction, distilled_text=distilled_text, text=text)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        return response

    def get_deduced_schema_code(self, instruction: str, text: str, distilled_text: str):
        prompt = deduced_schema_code_instruction.format(instruction=instruction, redefined_text=distilled_text, text=text)
        response = self.llm.get_chat_response(prompt)
        code_blocks = re.findall(r'```[^\n]*\n(.*?)\n```', response, re.DOTALL)
        if code_blocks:
            try:
                code_block = code_blocks[-1]
                namespace = {}
                exec(code_block, namespace)
                schema = namespace.get('ExtractionTarget')
                if schema is not None:
                    index = code_block.find("class")
                    code = code_block[index:]
                    print("Schema in Code: ", code)
                    schema = self.serialize_schema(schema)
                    return schema
            except Exception as e:
                print(e)
                return self.get_deduced_schema_json(instruction, text, distilled_text)
        return self.get_deduced_schema_json(instruction, text, distilled_text)

class SchemaAgent:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.module = SchemaAnalyzer(llm = llm)
        self.methods = ["get_default_schema", "get_retrieved_schema", "get_deduced_schema"]
        
    def __preprocess_text(self, data: DataPoint):
        if data.use_file:
            data.chunk_text_list = chunk_file(data.text)
        else:
            data.chunk_text_list = chunk_str(data.text)
        return data
             
    def get_default_schema(self, data: DataPoint):
        data = self.__preprocess_text(data)
        default_schema = config['agent']['default_schema']
        data.set_schema(default_schema)
        function_name = current_function_name()
        data.update_trajectory(function_name, default_schema)
        return data
    
    def get_retrieved_schema(self, data: DataPoint):
        self.__preprocess_text(data)
        schema_name = data.output_schema
        schema_class = globals().get(schema_name)
        if schema_class is not None:
            schema = self.module.serialize_schema(schema_class)
            data.set_schema(schema)
            function_name = current_function_name()
            data.update_trajectory(function_name, schema)
        else:
            return self.get_default_schema(data)
        return data
    
    def get_deduced_schema(self, data: DataPoint):
        self.__preprocess_text(data)
        target_text = data.chunk_text_list[0]
        analysed_text = self.module.get_text_analysis(analysed_text)
        distilled_text = self.module.redefine_text(target_text)
        deduced_schema = self.module.get_deduced_schema_code(data.instruction, target_text, distilled_text)
        data.set_distilled_text(distilled_text)
        data.set_schema(deduced_schema)
        function_name = current_function_name()
        data.update_trajectory(function_name, deduced_schema)
        return data
        