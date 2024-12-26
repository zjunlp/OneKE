import sys
sys.path.append("./src")
from models import *
from pipeline import *
import json

# model configuration
model = ChatGPT(model_name_or_path="gpt-4o-mini", api_key="sk-ADCiVBqVHAnnugtsGS2V05g2RigirBSoZc7unds4DWk3JPS3", base_url="https://api.chatanywhere.tech")
pipeline = Pipeline(model)

# extraction configuration
Task = "NER"
Text = "Finally , every other year , ELRA organizes a major conference LREC , the International Language Resources and Evaluation Conference ."
Constraint = ["nationality", "country capital", "place of death", "children", "location contains", "place of birth", "place lived", "administrative division of country", "country of administrative divisions", "company", "neighborhood of", "company founders"]

# get extraction result
result, trajectory = pipeline.get_extract_result(task=Task, text=Text, constraint=Constraint)
print("Trajectory:", json.dumps(trajectory, indent=4))

