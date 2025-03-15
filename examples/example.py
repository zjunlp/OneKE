import sys
sys.path.append("./src")
from models import *
from pipeline import *
import json

# model configuration
model = ChatGPT(model_name_or_path="your_model_name_or_path", api_key="your_api_key")
pipeline = Pipeline(model)

# extraction configuration
Task = "NER"
Text = "Finally , every other year , ELRA organizes a major conference LREC , the International Language Resources and Evaluation Conference."
Constraint = ["nationality", "country capital", "place of death", "children", "location contains", "place of birth", "place lived", "administrative division of country", "country of administrative divisions", "company", "neighborhood of", "company founders"]

# get extraction result
result, trajectory, frontend_schema, frontend_res = pipeline.get_extract_result(task=Task, text=Text, constraint=Constraint, show_trajectory=True)
