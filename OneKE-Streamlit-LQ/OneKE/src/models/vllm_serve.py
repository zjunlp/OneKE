import argparse
import warnings
import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

def main():
    # Create command-line argument parser
    parser = argparse.ArgumentParser(description='Run the extraction model.')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to the YAML configuration file.')
    parser.add_argument('--tensor-parallel-size', type=int, default=2,
                        help='Tensor parallel size for the VLLM server.')
    parser.add_argument('--max-model-len', type=int, default=32768,
                        help='Maximum model length for the VLLM server.')

    # Parse command-line arguments
    args = parser.parse_args()

    # Load configuration
    config = load_extraction_config(args.config)
    # Model config
    model_config = config['model']
    if model_config['vllm_serve'] == False:
        warnings.warn("VLLM-deployed model will not be used for extraction. To enable VLLM, set vllm_serve to true in the configuration file.")
    model_name_or_path = model_config['model_name_or_path']
    command = f"vllm serve {model_name_or_path} --tensor-parallel-size {args.tensor_parallel_size} --max-model-len {args.max_model_len} --enforce-eager --port 8000"
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()
