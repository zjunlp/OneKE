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
    def __init__(self, name=None, task="NER", data_dir = f"{DATA_DIR}/CrossNER", output_dir = f"{OUTPUT_DIR}", train=False):
        self.name = name
        self.task = task
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.test_file = json.load(open(f"{data_dir}/train.json")) if train else json.load(open(f"{data_dir}/test.json"))
        self.schema = str(json.load(open(f"{data_dir}/class.json")))
        self.retry = 2

    def evaluate(self, llm: BaseEngine, mode="", sample=None, random_sample=False, update_case=False):
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
            try:
                # get prediction
                num_items += 1
                truth = list(item.items())[1]
                truth = {truth[0]: truth[1]}
                pred_set = set()
                for attempt in range(self.retry):
                    pred_result, pred_detailed, _, _ = pipeline.get_extract_result(task=self.task, text=item['sentence'], constraint=self.schema, mode=mode, truth=truth, update_case=update_case)
                    try:
                        pred_result = pred_result['entity_list']
                        pred_set = dict_list_to_set(pred_result)
                        break
                    except Exception as e:
                        print(f"Failed to parse result: {pred_result}, retrying... Exception: {e}")

                # evaluate
                truth_result = item["entity_list"]
                truth_set = dict_list_to_set(truth_result)
                print(truth_set)
                print(pred_set)

                precision, recall, f1_score = calculate_metrics(truth_set, pred_set)
                total_precision += precision
                total_recall += recall
                total_f1 += f1_score

                pred_detailed["pred"] = pred_result
                pred_detailed["truth"] = truth_result
                pred_detailed["metrics"] = {"precision": precision, "recall": recall, "f1_score": f1_score}
                res_detailed = {"id": num_items}
                res_detailed.update(pred_detailed)
                with open(output_path, 'a') as file:
                    file.write(json.dumps(res_detailed) + '\n')
            except Exception as e:
                print(f"Exception occured: {e}")
                print(f"idx: {num_items}")
                pass

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
    def __init__(self, name=None, task="RE", data_dir = f"{DATA_DIR}/NYT11", output_dir = f"{OUTPUT_DIR}", train=False):
        self.name = name
        self.task = task
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.test_file = json.load(open(f"{data_dir}/train.json")) if train else json.load(open(f"{data_dir}/test.json"))
        self.schema = str(json.load(open(f"{data_dir}/class.json")))
        self.retry = 2

    def evaluate(self, llm: BaseEngine, mode="", sample=None, random_sample=False, update_case=False):
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
            try:
                # get prediction
                num_items += 1
                truth = list(item.items())[1]
                truth = {truth[0]: truth[1]}
                pred_set = set()
                for attempt in range(self.retry):
                    pred_result, pred_detailed, _, _ = pipeline.get_extract_result(task=self.task, text=item['sentence'], constraint=self.schema, mode=mode, truth=truth, update_case=update_case)
                    try:
                        pred_result = pred_result['relation_list']
                        pred_set = dict_list_to_set(pred_result)
                        break
                    except Exception as e:
                        print(f"Failed to parse result: {pred_result}, retrying... Exception: {e}")

                # evaluate
                truth_result = item["relation_list"]
                truth_set = dict_list_to_set(truth_result)
                print(truth_set)
                print(pred_set)

                precision, recall, f1_score = calculate_metrics(truth_set, pred_set)
                total_precision += precision
                total_recall += recall
                total_f1 += f1_score

                pred_detailed["pred"] = pred_result
                pred_detailed["truth"] = truth_result
                pred_detailed["metrics"] = {"precision": precision, "recall": recall, "f1_score": f1_score}
                res_detailed = {"id": num_items}
                res_detailed.update(pred_detailed)
                with open(output_path, 'a') as file:
                    file.write(json.dumps(res_detailed) + '\n')
            except Exception as e:
                print(f"Exception occured: {e}")
                print(f"idx: {num_items}")
                pass

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