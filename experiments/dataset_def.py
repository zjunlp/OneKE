import os
import json
import random
from utils import *
from pipeline import *
current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(current_dir, "../data/datasets")
OUTPUT_DIR = os.path.join(current_dir, "results")

class BaseDataset:
    def __init__(self):
        pass

    def __getitem__(self, idx):
        return None
    
    def __len__(self):
        return None
    
    def evaluate(self, idx, answer):
        return None

class NERDataset(BaseDataset):
    def __init__(self, name=None, task="NER", data_dir = f"{DATA_DIR}/FewNERD", output_dir = f"{OUTPUT_DIR}"):
        self.name = name
        self.task = task
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.test_file = json.load(open(f"{data_dir}/test.json"))
        self.schema = str(json.load(open(f"{data_dir}/schema.json")))
        self.retry = 2
    
    def evaluate(self, llm: BaseEngine, mode="", sample=None, random_sample=False):
        # initialize 
        sample = len(self.test_file) if sample is None else sample
        if random_sample:
            test_file = random.sample(self.test_file, sample)
        else:
            test_file = self.test_file[:sample]
        total_precision, total_recall, total_f1 = 0, 0, 0
        num_items = 0  
        output_path = f"{self.output_dir}/{self.name}_{self.task}_{mode}_reflection_{llm.name}_sample{sample}.jsonl"
        print("Results will be saved to: ", output_path)
        
        # predict and evaluate
        pipeline = Pipeline(llm=llm)
        for item in test_file:
            # get prediction
            truth = list(item.items())[1]
            truth = {truth[0]: truth[1]}  
            pred_set = set()  
            for attempt in range(self.retry):  
                pred_result, pred_detailed = pipeline.get_extract_result(task=self.task, text=item['sentence'], schema=self.schema, mode=mode, truth=truth)
                try:
                    pred_result = pred_result['entity_list']
                    pred_set = {(k, v) for k, v in pred_result.items()}
                    pred_set = {format_string(str(item)) for item in pred_set}
                    break  
                except Exception as e:
                    print(f"Failed to parse result: {pred_result}, retrying... Exception: {e}")

            # evaluate
            truth_result = item["entity_list"]
            truth_set = {(k, v) for k, v in truth_result.items()}
            truth_set = {format_string(str(item)) for item in truth_set}

            precision, recall, f1_score = calculate_metrics(truth_set, pred_set)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score
            num_items += 1  

            pred_detailed["pred"] = pred_result
            pred_detailed["truth"] = truth_result
            pred_detailed["metrics"] = {"precision": precision, "recall": recall, "f1_score": f1_score}
            res_detailed = {"id": num_items}
            res_detailed.update(pred_detailed)
            with open(output_path, 'a') as file:
                file.write(json.dumps(res_detailed) + '\n')

        pipeline.task.reflect_repo.update_corpus()
        
        # calculate overall metrics
        if num_items > 0:
            avg_precision = total_precision / num_items
            avg_recall = total_recall / num_items
            avg_f1 = total_f1 / num_items
            overall_metrics = {
                "total_items": num_items,
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1
            }
            with open(output_path, 'a') as file:
                file.write(json.dumps(overall_metrics) + '\n\n')
            print(f"Overall Metrics:\nTotal Items: {num_items}\nAverage Precision: {avg_precision:.4f}\nAverage Recall: {avg_recall:.4f}\nAverage F1 Score: {avg_f1:.4f}")
        else:
            print("No items processed.")
            
            
class REDataset(BaseDataset):
    def __init__(self, name=None, task="RE", data_dir = f"{DATA_DIR}/SemEval", output_dir = f"{OUTPUT_DIR}"):
        self.name = name
        self.task = task
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.test_file = json.load(open(f"{data_dir}/test.json"))
        self.schema = str(json.load(open(f"{data_dir}/schema.json")))
        self.retry = 2
    
    def dict_list_to_set(data_list):
        result_set = set()
        for dictionary in data_list:
            value_tuple = tuple(format_string(value) for value in dictionary.values())
            result_set.add(value_tuple)
        return result_set
    
    def evaluate(self, llm: BaseEngine, mode: ModeType, sample=None, random_sample=False):
        # initialize 
        sample = len(self.test_file) if sample is None else sample
        if random_sample:
            test_file = random.sample(self.test_file, sample)
        else:
            test_file = self.test_file[:sample]
        total_precision, total_recall, total_f1 = 0, 0, 0
        num_items = 0  
        output_path = f"{self.output_dir}/{self.name}_{self.task}_{mode}_{llm.name}_sample{sample}.jsonl"
        print("Results will be saved to: ", output_path)
        
        # predict and evaluate
        pipeline = Pipeline(llm=llm)
        for item in test_file:
            # get prediction
            truth = list(item.items())[1]
            truth = {truth[0]: truth[1]}  
            pred_set = set()  
            for attempt in range(self.retry):  
                pred_result, pred_detailed = pipeline.get_extract_result(task=self.task, text=item['sentence'], schema=self.schema, mode=mode, truth=truth)
                try:
                    pred_result = pred_result['relation_list']
                    pred_set = {(k, v) for k, v in pred_result.items()}
                    pred_set = {format_string(str(item)) for item in pred_set}
                    break  
                except Exception as e:
                    print(f"Failed to parse result: {pred_result}, retrying... Exception: {e}")

            # evaluate
            truth_result = item["entity_list"]
            truth_set = {(k, v) for k, v in truth_result.items()}
            truth_set = {format_string(str(item)) for item in truth_set}

            precision, recall, f1_score = calculate_metrics(truth_set, pred_set)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score
            num_items += 1  

            pred_detailed["pred"] = pred_result
            pred_detailed["truth"] = truth_result
            pred_detailed["metrics"] = {"precision": precision, "recall": recall, "f1_score": f1_score}
            res_detailed = {"id": num_items}
            res_detailed.update(pred_detailed)
            with open(output_path, 'a') as file:
                file.write(json.dumps(res_detailed) + '\n')

        pipeline.task.reflect_repo.update_corpus()
        
        # calculate overall metrics
        if num_items > 0:
            avg_precision = total_precision / num_items
            avg_recall = total_recall / num_items
            avg_f1 = total_f1 / num_items
            overall_metrics = {
                "total_items": num_items,
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1
            }
            with open(output_path, 'a') as file:
                file.write(json.dumps(overall_metrics) + '\n\n')
            print(f"Overall Metrics:\nTotal Items: {num_items}\nAverage Precision: {avg_precision:.4f}\nAverage Recall: {avg_recall:.4f}\nAverage F1 Score: {avg_f1:.4f}")
        else:
            print("No items processed.")
        
        