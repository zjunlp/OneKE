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
            schema_description = parser.get_format_instructions()
            schema_content = re.findall(r'```(.*?)```', schema_description, re.DOTALL)
            explanation = "For example, for the schema {\"properties\": {\"foo\": {\"title\": \"Foo\", \"description\": \"a list of strings\", \"type\": \"array\", \"items\": {\"type\": \"string\"}}}}, the object {\"foo\": [\"bar\", \"baz\"]} is a well-formatted instance."
            schema = f"{schema_content}\n\n{explanation}"
        except:
            return schema
        return schema

    def redefine_text(self, text_analysis):
        try:
            field = text_analysis['field']
            genre = text_analysis['genre']
        except:
            return text_analysis
        prompt = f"This text is from the field of {field} and represents the genre of {genre}."
        return prompt

    def get_text_analysis(self, text: str):
        output_schema = self.serialize_schema(schema_repository.TextDescription)
        prompt = text_analysis_instruction.format(examples="", text=text, schema=output_schema)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        response = self.redefine_text(response)
        return response

    def get_deduced_schema_json(self, instruction: str, text: str, distilled_text: str):
        prompt = deduced_schema_json_instruction.format(examples=example_wrapper(json_schema_examples), instruction=instruction, distilled_text=distilled_text, text=text)
        response = self.llm.get_chat_response(prompt)
        response = extract_json_dict(response)
        code = response
        print(f"Deduced Schema in Json: \n{response}\n\n")
        return code, response

    def get_deduced_schema_code(self, instruction: str, text: str, distilled_text: str):
        prompt = deduced_schema_code_instruction.format(examples=example_wrapper(code_schema_examples), instruction=instruction, distilled_text=distilled_text, text=text)
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
                    print(f"Deduced Schema in Code: \n{code}\n\n")
                    schema = self.serialize_schema(schema)
                    return code, schema
            except Exception as e:
                print(e)
                return self.get_deduced_schema_json(instruction, text, distilled_text)
        return self.get_deduced_schema_json(instruction, text, distilled_text)

class SchemaAgent:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.module = SchemaAnalyzer(llm = llm)
        self.schema_repo = schema_repository
        self.methods = ["get_default_schema", "get_retrieved_schema", "get_deduced_schema"]

    def __preprocess_text(self, data: DataPoint):
        if data.use_file:
            data.chunk_text_list = chunk_file(data.file_path)
        else:
            data.chunk_text_list = chunk_str(data.text)
        if data.task == "NER":
            data.print_schema = """
class Entity(BaseModel):
    name : str = Field(description="The specific name of the entity. ")
    type : str = Field(description="The type or category that the entity belongs to.")
class EntityList(BaseModel):
    entity_list : List[Entity] = Field(description="Named entities appearing in the text.")
            """
        elif data.task == "RE":
            data.print_schema = """
class Relation(BaseModel):
    head : str = Field(description="The starting entity in the relationship.")
    tail : str = Field(description="The ending entity in the relationship.")
    relation : str = Field(description="The predicate that defines the relationship between the two entities.")

class RelationList(BaseModel):
    relation_list : List[Relation] = Field(description="The collection of relationships between various entities.")
            """
        elif data.task == "EE":
            data.print_schema = """
class Event(BaseModel):
    event_type : str = Field(description="The type of the event.")
    event_trigger : str = Field(description="A specific word or phrase that indicates the occurrence of the event.")
    event_argument : dict = Field(description="The arguments or participants involved in the event.")

class EventList(BaseModel):
    event_list : List[Event] = Field(description="The events presented in the text.")
            """
        elif data.task == "Triple":
            data.print_schema = """
class Triple(BaseModel):
    head: str = Field(description="The subject or head of the triple.")
    head_type: str = Field(description="The type of the subject entity.")
    relation: str = Field(description="The predicate or relation between the entities.")
    relation_type: str = Field(description="The type of the relation.")
    tail: str = Field(description="The object or tail of the triple.")
    tail_type: str = Field(description="The type of the object entity.")
class TripleList(BaseModel):
    triple_list: List[Triple] = Field(description="The collection of triples and their types presented in the text.")
"""
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
        schema_class = getattr(self.schema_repo, schema_name, None)
        if schema_class is not None:
            schema = self.module.serialize_schema(schema_class)
            default_schema = config['agent']['default_schema']
            data.set_schema(f"{default_schema}\n{schema}")
            function_name = current_function_name()
            data.update_trajectory(function_name, schema)
        else:
            return self.get_default_schema(data)
        return data

    def get_deduced_schema(self, data: DataPoint):
        self.__preprocess_text(data)
        target_text = data.chunk_text_list[0]
        analysed_text = self.module.get_text_analysis(target_text)
        if len(data.chunk_text_list) > 1:
            prefix = "Below is a portion of the text to be extracted. "
            analysed_text = f"{prefix}\n{target_text}"
        distilled_text = self.module.redefine_text(analysed_text)
        code, deduced_schema = self.module.get_deduced_schema_code(data.instruction, target_text, distilled_text)
        data.print_schema = code
        data.set_distilled_text(distilled_text)
        default_schema = config['agent']['default_schema']
        data.set_schema(f"{default_schema}\n{deduced_schema}")
        function_name = current_function_name()
        data.update_trajectory(function_name, deduced_schema)
        return data
