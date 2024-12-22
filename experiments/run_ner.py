import sys
sys.path.append("./src")
from models import *
from dataset_def import *
name = "crossner-"
data_dir = "/disk/disk_20T/luoyujie/Agent/OneKE/OneKE-Agent/data/datasets/CrossNER/"
# model = LLaMA("/disk/disk_20T/share/Llama-3-8B-Instruct")
model = ChatGPT(model_name_or_path="gpt-4o-mini", api_key="sk-ADCiVBqVHAnnugtsGS2V05g2RigirBSoZc7unds4DWk3JPS3", base_url="https://api.chatanywhere.tech/v1")
tasklist = ["ai", "literature", "music"]
# tasklist = ["ai"]
for task in tasklist:
    task_name = name + task
    task_data_dir = data_dir + task
    dataset = NERDataset(name=task_name, data_dir=task_data_dir)
    mode = "standard"
    dataset.evaluate(llm=model, mode=mode, random_sample=True ,sample=1)
