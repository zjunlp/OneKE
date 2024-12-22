import sys
sys.path.append("./src")
from models import *
from dataset_def import *
data_dir = "/disk/disk_20T/luoyujie/Agent/OneKE/OneKE-Agent/data/datasets/NYT11/"
model = LLaMA("/disk/disk_20T/share/Llama-3-8B-Instruct")
# model = DeepSeek(model_name_or_path="deepseek-chat", api_key="sk-8a1ebfc920a145bea54a5ad6d987dbea")
dataset = REDataset(name="NYT11", data_dir=data_dir, train=True)
f1_score = dataset.evaluate(llm=model, mode="standard", sample=5)
print("f1_score: ", f1_score)

