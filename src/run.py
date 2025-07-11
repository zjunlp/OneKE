import argparse
import os
# import yaml
from pipeline import Pipeline
from typing import Literal
import models
from models import *
from utils import *
from modules import *
import os
import nltk
from datetime import datetime


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

        # save results to files
        save_results(result, trajectory, extraction_config)

        return
    else:
        print("please provide construct config in the yaml file.")

    result, trajectory, _, _ = pipeline.get_extract_result(task=extraction_config['task'], instruction=extraction_config['instruction'], text=extraction_config['text'], output_schema=extraction_config['output_schema'], constraint=extraction_config['constraint'], use_file=extraction_config['use_file'], file_path=extraction_config['file_path'], truth=extraction_config['truth'], mode=extraction_config['mode'], update_case=extraction_config['update_case'], show_trajectory=extraction_config['show_trajectory'])

    # save results to files
    save_results(result, trajectory, extraction_config)

    return

#save results to file
def save_results(result, trajectory, config):
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    task_type = config['task']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # result file
    result_path = os.path.join(output_dir, f"{task_type}_result_{timestamp}.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        # whether result is string
        if isinstance(result, str):
            try:
                # turn string to json
                parsed_result = json.loads(result)
                json.dump(parsed_result, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                f.write(result)
        else:
            # if dictionary/list
            json.dump(result, f, ensure_ascii=False, indent=2)

    # trajectory file
    if trajectory:
        traj_path = os.path.join(output_dir, f"{task_type}_trajectory_{timestamp}.json")
        with open(traj_path, 'w', encoding='utf-8') as f:
            json.dump(trajectory, f, ensure_ascii=False, indent=2)

    print(f"Extraction result has been saved in: {result_path}")
    if trajectory:
        print(f"Trajectory has been saved in: {traj_path}")

if __name__ == "__main__":
    main()
