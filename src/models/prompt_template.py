from langchain.prompts import PromptTemplate
from .prompt_example import *

# ==================================================================== #
#                           SCHEMA AGENT                               #
# ==================================================================== #

# Get Text Analysis
TEXT_ANALYSIS_INSTRUCTION = """
**Instruction**: Please analyze and categorize the given text.
{examples}
**Text**: {text}

**Output Shema**: {schema}
"""

text_analysis_instruction = PromptTemplate(
    input_variables=["examples", "text", "schema"],
    template=TEXT_ANALYSIS_INSTRUCTION,
)

# Get Deduced Schema Json
DEDUCE_SCHEMA_JSON_INSTRUCTION = """
**Instruction**: Generate an output format that meets the requirements as described in the task. Pay attention to the following requirements:
    - Format: Return your responses in dictionary format as a JSON object.
    - Content: Do not include any actual data; all attributes values should be set to None.
    - Note: Attributes not mentioned in the task description should be ignored.
{examples}
**Task**: {instruction}

**Text**: {distilled_text}
{text}

Now please deduce the output schema in json format. All attributes values should be set to None.
**Output Schema**:
"""

deduced_schema_json_instruction = PromptTemplate(
    input_variables=["examples", "instruction", "distilled_text", "text", "schema"],
    template=DEDUCE_SCHEMA_JSON_INSTRUCTION,
)

# Get Deduced Schema Code
DEDUCE_SCHEMA_CODE_INSTRUCTION = """
**Instruction**: Based on the provided text and task description, Define the output schema in Python using Pydantic. Name the final extraction target class as 'ExtractionTarget'.
{examples}
**Task**: {instruction}

**Text**: {distilled_text}
{text}

Now please deduce the output schema. Ensure that the output code snippet is wrapped in '```',and can be directly parsed by the Python interpreter.
**Output Schema**: """
deduced_schema_code_instruction = PromptTemplate(
    input_variables=["examples", "instruction", "distilled_text", "text"],
    template=DEDUCE_SCHEMA_CODE_INSTRUCTION,
)


# ==================================================================== #
#                         EXTRACTION AGENT                             #
# ==================================================================== #

EXTRACT_INSTRUCTION = """
**Instruction**: You are an agent skilled in information extarction. {instruction}
{examples}
**Text**: {text}
{additional_info}
**Output Schema**: {schema}

Now please extract the corresponding information from the text. Ensure that the information you extract has a clear reference in the given text. Set any property not explicitly mentioned in the text to null.
"""

extract_instruction = PromptTemplate(
    input_variables=["instruction", "examples", "text", "schema", "additional_info"],
    template=EXTRACT_INSTRUCTION,
)

instruction_mapper = {
    'NER': "You are an expert in named entity recognition. Please extract entities that match the schema definition from the input. Return an empty list if the entity type does not exist. Please respond in the format of a JSON string.",
    'RE': "You are an expert in relationship extraction. Please extract relationship triples that match the schema definition from the input. Return an empty list for relationships that do not exist. Please respond in the format of a JSON string.",
    'EE': "You are an expert in event extraction. Please extract events from the input that conform to the schema definition. Return an empty list for events that do not exist, and return NAN for arguments that do not exist. If an argument has multiple values, please return a list. Respond in the format of a JSON string.",
}

EXTRACT_INSTRUCTION_JSON = """
{{
    "instruction": {instruction},
    "schema": {constraint},
    "input": {input},
}}
"""

extract_instruction_json = PromptTemplate(
    input_variables=["instruction", "constraint", "input"],
    template=EXTRACT_INSTRUCTION_JSON,
)

SUMMARIZE_INSTRUCTION = """
**Instruction**: Below is a list of results obtained after segmenting and extracting information from a long article. Please consolidate all the answers to generate a final response.
{examples}
**Task**: {instruction}

**Result List**: {answer_list}

**Output Schema**: {schema}
Now summarize all the information from the Result List. Filter or merge the redundant information.
"""
summarize_instruction = PromptTemplate(
    input_variables=["instruction", "examples", "answer_list", "schema"],
    template=SUMMARIZE_INSTRUCTION,
)




# ==================================================================== #
#                          REFLECION AGENT                             #
# ==================================================================== #
REFLECT_INSTRUCTION = """**Instruction**: You are an agent skilled in reflection and optimization based on the original result. Refer to **Reflection Reference** to identify potential issues in the current extraction results.

**Reflection Reference**: {examples}

Now please review each element in the extraction result. Identify and improve any potential issues in the result based on the reflection. NOTE: If the original result is correct, no modifications are needed!

**Task**: {instruction}

**Text**: {text}

**Output Schema**: {schema}

**Original Result**: {result}

"""
reflect_instruction = PromptTemplate(
    input_variables=["instruction", "examples", "text", "schema", "result"],
    template=REFLECT_INSTRUCTION,
)

SUMMARIZE_INSTRUCTION = """
**Instruction**: Below is a list of results obtained after segmenting and extracting information from a long article. Please consolidate all the answers to generate a final response.

**Task**: {instruction}

**Result List**: {answer_list}
{additional_info}
**Output Schema**: {schema}
Now summarize the information from the Result List.
"""
summarize_instruction = PromptTemplate(
    input_variables=["instruction", "answer_list", "additional_info", "schema"],
    template=SUMMARIZE_INSTRUCTION,
)



# ==================================================================== #
#                            CASE REPOSITORY                           #
# ==================================================================== #

GOOD_CASE_ANALYSIS_INSTRUCTION = """
**Instruction**: Below is an information extraction task and its corresponding correct answer. Provide the reasoning steps that led to the correct answer, along with brief explanation of the answer. Your response should be brief and organized.

**Task**: {instruction}

**Text**: {text}
{additional_info}
**Correct Answer**: {result}

Now please generate the reasoning steps and breif analysis of the **Correct Answer** given above. DO NOT generate your own extraction result.
**Analysis**:
"""
good_case_analysis_instruction = PromptTemplate(
    input_variables=["instruction", "text", "result", "additional_info"],
    template=GOOD_CASE_ANALYSIS_INSTRUCTION,
)

BAD_CASE_REFLECTION_INSTRUCTION = """
**Instruction**: Based on the task description, compare the original answer with the correct one. Your output should be a brief reflection or concise summarized rules.

**Task**: {instruction}

**Text**: {text}
{additional_info}
**Original Answer**: {original_answer}

**Correct Answer**: {correct_answer}

Now please generate a brief and organized reflection. DO NOT generate your own extraction result.
**Reflection**:
"""

bad_case_reflection_instruction = PromptTemplate(
    input_variables=["instruction", "text", "original_answer", "correct_answer", "additional_info"],
    template=BAD_CASE_REFLECTION_INSTRUCTION,
)