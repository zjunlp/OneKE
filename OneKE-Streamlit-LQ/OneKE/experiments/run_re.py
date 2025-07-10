import sys
sys.path.append("./src")
from models import *
from dataset_def import *
data_dir = "./data/datasets/NYT11/"
model = LLaMA("meta-llama/Meta-Llama-3-8B-Instruct")
dataset = REDataset(name="NYT11", data_dir=data_dir)
f1_score = dataset.evaluate(llm=model, mode="quick")
print("f1_score: ", f1_score)

