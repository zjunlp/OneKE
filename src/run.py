import argparse
import os
import yaml
from pipeline import Pipeline
from typing import Literal
import models
from models import *
from utils import *
from modules import *

def load_extraction_config(yaml_path):
    # 从文件路径读取 YAML 内容
    if not os.path.exists(yaml_path):
        print(f"Error: The config file '{yaml_path}' does not exist.")
        return {}
        
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)

    # 提取'extraction'配置的字典
    model_config = config.get('model', {})
    extraction_config = config.get('extraction', {})
    # model config
    model_name_or_path = model_config.get('model_name_or_path', "")
    model_category = model_config.get('category', "")
    api_key = model_config.get('api_key', "")
    base_url = model_config.get('base_url', "")
    
    # extraction config
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

    # 返回一个包含这些变量的字典
    return {
        "model": {
            "model_name_or_path": model_name_or_path,
            "category": model_category,
            "api_key": api_key,
            "base_url": base_url
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
            "update_case": update_case
        }
    }


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Run the extraction model.')
    parser.add_argument('--config', type=str, required=True, 
                        help='Path to the YAML configuration file.')

    # 解析命令行参数
    args = parser.parse_args()

    # 加载配置
    config = load_extraction_config(args.config)
    model_config = config['model']
    extraction_config = config['extraction']
    clazz = getattr(models, model_config['category'], None)
    if clazz is None:
        print(f"Error: The model category '{model_config['category']}' is not supported.")
        return
    if model_config['api_key'] == "":
        model = clazz(model_config['model_name_or_path'])
    else:
        model = clazz(model_config['model_name_or_path'], model_config['api_key'], model_config['base_url'])
    pipeline = Pipeline(model)
    result, trajectory = pipeline.get_extract_result(task=extraction_config['task'], instruction=extraction_config['instruction'], text=extraction_config['text'], output_schema=extraction_config['output_schema'], constraint=extraction_config['constraint'], use_file=extraction_config['use_file'], file_path=extraction_config['file_path'],truth=extraction_config['truth'], mode=extraction_config['mode'], update_case=extraction_config['update_case'])
    return 

if __name__ == "__main__":
    main()
