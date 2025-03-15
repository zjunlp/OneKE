import json
import os
import torch
import numpy as np
from utils import *
from sentence_transformers import SentenceTransformer
from rapidfuzz import process
from models import *
import copy

import warnings
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
docker_model_path = "/app/model/all-MiniLM-L6-v2"
warnings.filterwarnings("ignore", category=FutureWarning, message=r".*clean_up_tokenization_spaces*")

class CaseRepository:
    def __init__(self):
        try:
            self.embedder = SentenceTransformer(docker_model_path)
        except:
            self.embedder = SentenceTransformer(config['model']['embedding_model'])
        self.embedder.to(device)
        self.corpus = self.load_corpus()
        self.embedded_corpus = self.embed_corpus()

    def load_corpus(self):
        with open(os.path.join(os.path.dirname(__file__), "case_repository.json")) as file:
            corpus = json.load(file)
        return corpus

    def update_corpus(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "case_repository.json"), "w") as file:
                json.dump(self.corpus, file, indent=2)
        except Exception as e:
            print(f"Error when updating corpus: {e}")

    def embed_corpus(self):
        embedded_corpus = {}
        for key, content in self.corpus.items():
            good_index = [item['index']['embed_index'] for item in content['good']]
            encoded_good_index = self.embedder.encode(good_index, convert_to_tensor=True).to(device)
            bad_index = [item['index']['embed_index'] for item in content['bad']]
            encoded_bad_index = self.embedder.encode(bad_index, convert_to_tensor=True).to(device)
            embedded_corpus[key] = {"good": encoded_good_index, "bad": encoded_bad_index}
        return embedded_corpus

    def get_similarity_scores(self, task: TaskType, embed_index="", str_index="", case_type="", top_k=2):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Embedding similarity match
        encoded_embed_query = self.embedder.encode(embed_index, convert_to_tensor=True).to(device)
        embedding_similarity_matrix = self.embedder.similarity(encoded_embed_query, self.embedded_corpus[task][case_type])
        embedding_similarity_scores = embedding_similarity_matrix[0].to(device)

        # String similarity match
        str_match_corpus = [item['index']['str_index'] for item in self.corpus[task][case_type]]
        str_similarity_results = process.extract(str_index, str_match_corpus, limit=len(str_match_corpus))
        scores_dict = {match[0]: match[1] for match in str_similarity_results}
        scores_in_order = [scores_dict[candidate] for candidate in str_match_corpus]
        str_similarity_scores = torch.tensor(scores_in_order, dtype=torch.float32).to(device)

        # Normalize scores
        embedding_score_range = embedding_similarity_scores.max() - embedding_similarity_scores.min()
        str_score_range = str_similarity_scores.max() - str_similarity_scores.min()
        if embedding_score_range > 0:
            embed_norm_scores = (embedding_similarity_scores - embedding_similarity_scores.min()) / embedding_score_range
        else:
            embed_norm_scores = embedding_similarity_scores
        if str_score_range > 0:
            str_norm_scores = (str_similarity_scores - str_similarity_scores.min()) / str_score_range
        else:
            str_norm_scores = str_similarity_scores / 100

        # Combine the scores with weights
        combined_scores = 0.5 * embed_norm_scores + 0.5 * str_norm_scores
        original_combined_scores = 0.5 * embedding_similarity_scores + 0.5 * str_similarity_scores / 100

        scores, indices = torch.topk(combined_scores, k=min(top_k, combined_scores.size(0)))
        original_scores, original_indices = torch.topk(original_combined_scores, k=min(top_k, original_combined_scores.size(0)))
        return scores, indices, original_scores, original_indices

    def query_case(self, task: TaskType, embed_index="", str_index="", case_type="", top_k=2) -> list:
        _, indices, _, _ = self.get_similarity_scores(task, embed_index, str_index, case_type, top_k)
        top_matches = [self.corpus[task][case_type][idx]["content"] for idx in indices]
        return top_matches

    def update_case(self, task: TaskType, embed_index="", str_index="", content="" ,case_type=""):
        self.corpus[task][case_type].append({"index": {"embed_index": embed_index, "str_index": str_index}, "content": content})
        self.embedded_corpus[task][case_type] = torch.cat([self.embedded_corpus[task][case_type], self.embedder.encode([embed_index], convert_to_tensor=True).to(device)], dim=0)
        print(f"A {case_type} case updated for {task} task.")

class CaseRepositoryHandler:
    def __init__(self, llm: BaseEngine):
        self.repository = CaseRepository()
        self.llm = llm

    def __get_good_case_analysis(self, instruction="", text="", result="", additional_info=""):
        prompt = good_case_analysis_instruction.format(
            instruction=instruction, text=text, result=result, additional_info=additional_info
        )
        for _ in range(3):
            response = self.llm.get_chat_response(prompt)
            response = extract_json_dict(response)
            if not isinstance(response, dict):
                return response
        return None

    def __get_bad_case_reflection(self, instruction="", text="", original_answer="", correct_answer="", additional_info=""):
        prompt = bad_case_reflection_instruction.format(
            instruction=instruction, text=text, original_answer=original_answer, correct_answer=correct_answer, additional_info=additional_info
        )
        for _ in range(3):
            response = self.llm.get_chat_response(prompt)
            response = extract_json_dict(response)
            if not isinstance(response, dict):
                return response
        return None

    def __get_index(self, data: DataPoint, case_type: str):
        # set embed_index
        embed_index = f"**Text**: {data.distilled_text}\n{data.chunk_text_list[0]}"

        # set str_index
        if data.task == "Base":
            str_index = f"**Task**: {data.instruction}"
        else:
            str_index = f"{data.constraint}"

        if case_type == "bad":
            str_index += f"\n\n**Original Result**: {json.dumps(data.pred)}"

        return embed_index, str_index

    def query_good_case(self, data: DataPoint):
        embed_index, str_index = self.__get_index(data, "good")
        return self.repository.query_case(task=data.task, embed_index=embed_index, str_index=str_index, case_type="good")

    def query_bad_case(self, data: DataPoint):
        embed_index, str_index = self.__get_index(data, "bad")
        return self.repository.query_case(task=data.task, embed_index=embed_index, str_index=str_index, case_type="bad")

    def update_good_case(self, data: DataPoint):
        if data.truth == "" :
            print("No truth value provided.")
            return
        embed_index, str_index = self.__get_index(data, "good")
        _, _, original_scores, _ = self.repository.get_similarity_scores(data.task, embed_index, str_index, "good", 1)
        original_scores = original_scores.tolist()
        if original_scores[0] >= 0.9:
            print("The similar good case is already in the corpus. Similarity Score: ", original_scores[0])
            return
        good_case_alaysis = self.__get_good_case_analysis(instruction=data.instruction, text=data.distilled_text, result=data.truth, additional_info=data.constraint)
        wrapped_good_case_analysis = f"**Analysis**: {good_case_alaysis}"
        wrapped_instruction = f"**Task**: {data.instruction}"
        wrapped_text = f"**Text**: {data.distilled_text}\n{data.chunk_text_list[0]}"
        wrapped_answer = f"**Correct Answer**: {json.dumps(data.truth)}"
        if data.task == "Base":
            content = f"{wrapped_instruction}\n\n{wrapped_text}\n\n{wrapped_good_case_analysis}\n\n{wrapped_answer}"
        else:
            content = f"{wrapped_text}\n\n{data.constraint}\n\n{wrapped_good_case_analysis}\n\n{wrapped_answer}"
        self.repository.update_case(data.task, embed_index, str_index, content, "good")

    def update_bad_case(self, data: DataPoint):
        if data.truth == "" :
            print("No truth value provided.")
            return
        if normalize_obj(data.pred) == normalize_obj(data.truth):
            return
        embed_index, str_index = self.__get_index(data, "bad")
        _, _, original_scores, _ = self.repository.get_similarity_scores(data.task, embed_index, str_index, "bad", 1)
        original_scores = original_scores.tolist()
        if original_scores[0] >= 0.9:
            print("The similar bad case is already in the corpus. Similarity Score: ", original_scores[0])
            return
        bad_case_reflection = self.__get_bad_case_reflection(instruction=data.instruction, text=data.distilled_text, original_answer=data.pred, correct_answer=data.truth, additional_info=data.constraint)
        wrapped_bad_case_reflection = f"**Reflection**: {bad_case_reflection}"
        wrapper_original_answer = f"**Original Answer**: {json.dumps(data.pred)}"
        wrapper_correct_answer = f"**Correct Answer**: {json.dumps(data.truth)}"
        wrapped_instruction = f"**Task**: {data.instruction}"
        wrapped_text = f"**Text**: {data.distilled_text}\n{data.chunk_text_list[0]}"
        if data.task == "Base":
            content = f"{wrapped_instruction}\n\n{wrapped_text}\n\n{wrapper_original_answer}\n\n{wrapped_bad_case_reflection}\n\n{wrapper_correct_answer}"
        else:
            content =  f"{wrapped_text}\n\n{data.constraint}\n\n{wrapper_original_answer}\n\n{wrapped_bad_case_reflection}\n\n{wrapper_correct_answer}"
        self.repository.update_case(data.task, embed_index, str_index, content, "bad")

    def update_case(self, data: DataPoint):
        self.update_good_case(data)
        self.update_bad_case(data)
        self.repository.update_corpus()