"""
Data Processing Functions.
Supports:
- Segmentation of long text
- Segmentation of file content
"""
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader, BSHTMLLoader, JSONLoader
from nltk.tokenize import sent_tokenize
from collections import Counter
import re
import json
import yaml
import os
import yaml
import os
import inspect
import ast
with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml")) as file:
    config = yaml.safe_load(file)

# Load configuration
def load_extraction_config(yaml_path):
    # Read YAML content from the file path
    if not os.path.exists(yaml_path):
        print(f"Error: The config file '{yaml_path}' does not exist.")
        return {}

    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)

    # Extract the 'extraction' configuration dictionary
    model_config = config.get('model', {})
    extraction_config = config.get('extraction', {})

    # Model config
    model_name_or_path = model_config.get('model_name_or_path', "")
    model_category = model_config.get('category', "")
    api_key = model_config.get('api_key', "")
    base_url = model_config.get('base_url', "")
    vllm_serve = model_config.get('vllm_serve', False)

    # Extraction config
    task = extraction_config.get('task', "")
    instruction = extraction_config.get('instruction', "")
    text = extraction_config.get('text', "")
    output_schema = extraction_config.get('output_schema', "")
    constraint = extraction_config.get('constraint', "")
    truth = extraction_config.get('truth', "")
    use_file = extraction_config.get('use_file', False)
    file_path = extraction_config.get('file_path', "")
    mode = extraction_config.get('mode', "quick")
    update_case = extraction_config.get('update_case', False)
    show_trajectory = extraction_config.get('show_trajectory', False)

    # Construct config (optional: for constructing your knowledge graph)
    if 'construct' in config:
        construct_config = config.get('construct', {})
        database = construct_config.get('database', "")
        url = construct_config.get('url', "")
        username = construct_config.get('username', "")
        password = construct_config.get('password', "")
        # Return a dictionary containing these variables
        return {
            "model": {
                "model_name_or_path": model_name_or_path,
                "category": model_category,
                "api_key": api_key,
                "base_url": base_url,
                "vllm_serve": vllm_serve
            },
            "extraction": {
                "task": task,
                "instruction": instruction,
                "text": text,
                "output_schema": output_schema,
                "constraint": constraint,
                "truth": truth,
                "use_file": use_file,
                "file_path": file_path,
                "mode": mode,
                "update_case": update_case,
                "show_trajectory": show_trajectory
            },
            "construct": {
                "database": database,
                "url": url,
                "username": username,
                "password": password
            }
        }

    # Return a dictionary containing these variables
    return {
        "model": {
            "model_name_or_path": model_name_or_path,
            "category": model_category,
            "api_key": api_key,
            "base_url": base_url,
            "vllm_serve": vllm_serve
        },
        "extraction": {
            "task": task,
            "instruction": instruction,
            "text": text,
            "output_schema": output_schema,
            "constraint": constraint,
            "truth": truth,
            "use_file": use_file,
            "file_path": file_path,
            "mode": mode,
            "update_case": update_case,
            "show_trajectory": show_trajectory
        }
    }

# Split the string text into chunks
def chunk_str(text):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        token_count = len(sentence.split())
        if current_length + token_count <= config['agent']['chunk_token_limit']:
            current_chunk.append(sentence)
            current_length += token_count
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = token_count
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

# Load and split the content of a file
def chunk_file(file_path):
    pages = []

    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".html"):
        loader = BSHTMLLoader(file_path)
    elif file_path.endswith(".json"):
        loader = JSONLoader(file_path)
    else:
        raise ValueError("Unsupported file format")  # Inform that the format is unsupported

    pages = loader.load_and_split()
    docs = ""
    for item in pages:
        docs += item.page_content
    pages = chunk_str(docs)

    return pages

def process_single_quotes(text):
    result = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
    return result

def remove_empty_values(data):
    def is_empty(value):
        return value is None or value == [] or value == "" or value == {}
    if isinstance(data, dict):
        return {
            k: remove_empty_values(v)
            for k, v in data.items()
            if not is_empty(v)
        }
    elif isinstance(data, list):
        return [
            remove_empty_values(item)
            for item in data
            if not is_empty(item)
        ]
    else:
        return data

def extract_json_dict(text):
    if isinstance(text, dict):
        return text
    pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\})*)*\})*)*\}'
    matches = re.findall(pattern, text)
    if matches:
        json_string = matches[-1]
        json_string = process_single_quotes(json_string)
        try:
            json_dict = json.loads(json_string)
            json_dict = remove_empty_values(json_dict)
            if json_dict is None:
                return "No valid information found."
            return json_dict
        except json.JSONDecodeError:
            return json_string
    else:
        return text

def good_case_wrapper(example: str):
    if example is None or example == "":
        return ""
    example = f"\nHere are some examples:\n{example}\n(END OF EXAMPLES)\nRefer to the reasoning steps and analysis in the examples to help complete the extraction task below.\n\n"
    return example

def bad_case_wrapper(example: str):
    if example is None or example == "":
        return ""
    example = f"\nHere are some examples of bad cases:\n{example}\n(END OF EXAMPLES)\nRefer to the reflection rules and reflection steps in the examples to help optimize the original result below.\n\n"
    return example

def example_wrapper(example: str):
    if example is None or example == "":
        return ""
    example = f"\nHere are some examples:\n{example}\n(END OF EXAMPLES)\n\n"
    return example

def remove_redundant_space(s):
    s = ' '.join(s.split())
    s = re.sub(r"\s*(,|:|\(|\)|\.|_|;|'|-)\s*", r'\1', s)
    return s

def format_string(s):
    s = remove_redundant_space(s)
    s = s.lower()
    s = s.replace('{','').replace('}','')
    s = re.sub(',+', ',', s)
    s = re.sub('\.+', '.', s)
    s = re.sub(';+', ';', s)
    s = s.replace('’', "'")
    return s

def calculate_metrics(y_truth: set, y_pred: set):
    TP = len(y_truth & y_pred)
    FN = len(y_truth - y_pred)
    FP = len(y_pred - y_truth)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1_score

def current_function_name():
    try:
        stack = inspect.stack()
        if len(stack) > 1:
            outer_func_name = stack[1].function
            return outer_func_name
        else:
            print("No caller function found")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        pass

def normalize_obj(value):
    if isinstance(value, dict):
        return frozenset((k, normalize_obj(v)) for k, v in value.items())
    elif isinstance(value, (list, set, tuple)):
        return tuple(Counter(map(normalize_obj, value)).items())
    elif isinstance(value, str):
        return format_string(value)
    return value

def dict_list_to_set(data_list):
    result_set = set()
    try:
        for dictionary in data_list:
            value_tuple = tuple(format_string(value) for value in dictionary.values())
            result_set.add(value_tuple)
        return result_set
    except Exception as e:
        print (f"Failed to convert dictionary list to set: {data_list}")
        return result_set
