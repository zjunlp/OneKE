from typing import Literal
from models import *
from .process import *
# predefined processing logic for routine extraction tasks
TaskType = Literal["NER", "RE", "EE", "Base"]

class DataPoint:
    def __init__(self,
                 task: TaskType = "Base",
                 instruction: str = "",
                 text: str = "",
                 output_schema: str = "",
                 constraint: str = "",
                 use_file: bool = False,
                 file_path: str = "",
                 truth: str = ""):
        """
        Initialize a DataPoint instance.
        """
        # task information
        self.task = task
        self.instruction = instruction
        self.text = text
        self.output_schema = output_schema
        self.constraint = constraint
        self.use_file = use_file
        self.file_path = file_path
        self.truth = extract_json_dict(truth)
        # temp storage
        self.print_schema = ""
        self.distilled_text = ""
        self.chunk_text_list = []
        # result feedback
        self.result_list = []
        self.result_trajectory = {}
        self.pred = ""

    def set_constraint(self, constraint):
        self.constraint = constraint

    def set_schema(self, output_schema):
        self.output_schema = output_schema

    def set_pred(self, pred):
        self.pred = pred

    def set_result_list(self, result_list):
        self.result_list = result_list

    def set_distilled_text(self, distilled_text):
        self.distilled_text = distilled_text

    def update_trajectory(self, function, result):
        if function not in self.result_trajectory:
            self.result_trajectory.update({function: result})

    def get_result_trajectory(self):
        return {"instruction": self.instruction, "text": self.text, "constraint": self.constraint,  "trajectory": self.result_trajectory, "pred": self.pred}
