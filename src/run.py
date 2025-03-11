import argparse
import os
import yaml
from pipeline import Pipeline
from typing import Literal
import models
from models import *
from utils import *
from modules import *

def main():
    # Create command-line argument parser
    parser = argparse.ArgumentParser(description='Run the extraction framefork.')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to the YAML configuration file.')

    # Parse command-line arguments
    args = parser.parse_args()

    # Load configuration
    config = load_extraction_config(args.config)
    # Model config
    model_config = config['model']
    if model_config['vllm_serve'] == True:
        model = LocalServer(model_config['model_name_or_path'])
    else:
        clazz = getattr(models, model_config['category'], None)
        if clazz is None:
            print(f"Error: The model category '{model_config['category']}' is not supported.")
            return
        if model_config['api_key'] == "":
            model = clazz(model_config['model_name_or_path'])
        else:
            model = clazz(model_config['model_name_or_path'], model_config['api_key'], model_config['base_url'])
    pipeline = Pipeline(model)
    # Extraction config
    extraction_config = config['extraction']
    # constuct config
    if 'construct' in config:
        construct_config = config['construct']
        result, trajectory, _, _ = pipeline.get_extract_result(task=extraction_config['task'], instruction=extraction_config['instruction'], text=extraction_config['text'], output_schema=extraction_config['output_schema'], constraint=extraction_config['constraint'], use_file=extraction_config['use_file'], file_path=extraction_config['file_path'], truth=extraction_config['truth'], mode=extraction_config['mode'], update_case=extraction_config['update_case'], show_trajectory=extraction_config['show_trajectory'],
                                                               construct=construct_config, iskg=True) # When 'construct' is provided, 'iskg' should be True to construct the knowledge graph.
        return
    else:
        print("please provide construct config in the yaml file.")

    result, trajectory, _, _ = pipeline.get_extract_result(task=extraction_config['task'], instruction=extraction_config['instruction'], text=extraction_config['text'], output_schema=extraction_config['output_schema'], constraint=extraction_config['constraint'], use_file=extraction_config['use_file'], file_path=extraction_config['file_path'], truth=extraction_config['truth'], mode=extraction_config['mode'], update_case=extraction_config['update_case'], show_trajectory=extraction_config['show_trajectory'])
    return

if __name__ == "__main__":
    main()
