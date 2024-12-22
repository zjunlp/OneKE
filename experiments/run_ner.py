import sys
sys.path.append("./src")
from models import *
from dataset_def import *
name = "crossner-"
data_dir = "./data/datasets/CrossNER/"
model = ChatGPT(model_name_or_path="gpt-4o-mini", api_key="your_api_key", base_url=" https://api.openai.com/v1")
tasklist = ["ai", "literature", "music", "politics", "science"]
for task in tasklist:
    task_name = name + task
    task_data_dir = data_dir + task
    dataset = NERDataset(name=task_name, data_dir=task_data_dir)
    mode = "quick"
    f1_score = dataset.evaluate(llm=model, mode=mode)
    print(f"Task: {task_name}, f1_score: {f1_score}")
