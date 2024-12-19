import json
import os
import torch
import numpy as np
from utils import *
from sentence_transformers import SentenceTransformer
from rapidfuzz import process
from models import *
import copy

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class CaseRepository:
    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
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
            print("Corpus updated.")
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
        embedding_similarity_scores = embedding_similarity_matrix[0]

        # String similarity match
        str_match_corpus = [item['index']['str_index'] for item in self.corpus[task][case_type]]
        str_similarity_results = process.extract(str_index, str_match_corpus, limit=len(str_match_corpus))
        str_similarity_scores = torch.tensor([score for _, score, _ in str_similarity_results], dtype=torch.float32)

        # Normalize scores
        embed_norm_scores = (embedding_similarity_scores - embedding_similarity_scores.min()) / (embedding_similarity_scores.max() - embedding_similarity_scores.min())
        str_norm_scores = (str_similarity_scores - str_similarity_scores.min()) / (str_similarity_scores.max() - str_similarity_scores.min())

        # Combine the scores with weights
        combined_scores = 0.5 * embed_norm_scores + 0.5 * str_norm_scores
        scores, indices = torch.topk(combined_scores, k=min(top_k, combined_scores.size(0)))
        return scores, indices
    
    def query_case(self, task: TaskType, embed_index="", str_index="", case_type="", top_k=2) -> list:
        scores, indices = self.get_similarity_scores(task, embed_index, str_index, case_type, top_k)
        top_matches = [self.corpus[case_type][idx]["content"] for idx in indices]
        return top_matches
        
    def update_case(self, task: TaskType, embed_index="", str_index="", content="" ,case_type=""):
        self.corpus[task][case_type].append({"index": {"embed_index": embed_index, "str_index": str_index}, "content": content})

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
        
    def __get_index(self, data: DataPoint):
        if data.task == "Base":
            embed_index = f"**Text**: {data.distilled_text}\n{data.chunk_text_list[0]}"
            str_index = f"**Task**: {data.instruction}"
        else:
            constraint = json.dumps(data.constraint)
            embed_index = f"**Text**: {data.distilled_text}\n{data.chunk_text_list[0]}"
            str_index = f"{constraint}"
        return embed_index, str_index
    
    def query_good_case(self, data: DataPoint):
        embed_index, str_index = self.__get_index(data)
        return self.repository.query_case(task=data.task, embed_index=embed_index, str_index=str_index, case_type="good")
    
    def query_bad_case(self, data: DataPoint):
        embed_index, str_index = self.__get_index(data)
        return self.repository.query_case(task=data.task, embed_index=embed_index, str_index=str_index, case_type="bad")
    
    def update_good_case(self, data: DataPoint):
        if data.truth == "":
            return 
        embed_index, str_index = self.__get_index(data)
        scores, indices = self.repository.get_similarity_scores(data.task, embed_index, str_index, "good", 1)
        scores = scores.tolist()
        if scores[0] >= 0.9:
            print("The similar good case is already in the corpus.")
            return
        good_case_alaysis = self.__get_good_case_analysis(instruction=data.instruction, text=data.distilled_text, result=data.truth, additional_info=data.constraint)
        wrapped_good_case_analysis = f"**Analysis**: {good_case_alaysis}"
        wrapped_answer = f"**Correct Answer**: {data.truth}"
        content = f"{str_index}\n\n{embed_index}\n\n{wrapped_good_case_analysis}\n\n{wrapped_answer}"
        self.repository.update_case(data.task, embed_index, str_index, content, "good")
    
    def update_bad_case(self, data: DataPoint):
        if data.truth == "" or normalize_obj(data.pred) == normalize_obj(data.truth):
            return 
        embed_index, str_index = self.__get_index(data)
        scores, indices = self.repository.get_similarity_scores(data.task, embed_index, str_index, "good", 1)
        scores = scores.tolist()
        if scores[0] >= 0.9:
            print("The similar bad case is already in the corpus.")
            return
        bad_case_reflection = self.__get_bad_case_reflection(instruction=data.instruction, text=data.distilled_text, original_answer=data.pred, correct_answer=data.truth, additional_info=data.constraint)
        wrapped_bad_case_reflection = f"**Reflection**: {bad_case_reflection}"
        wrapper_original_answer = f"**Original Answer**: {data.pred}"
        wrapper_correct_answer = f"**Correct Answer**: {data.truth}"
        content = f"{str_index}\n\n{embed_index}\n\n{wrapper_original_answer}\n\n{wrapped_bad_case_reflection}\n\n{wrapper_correct_answer}"
        self.repository.update_case(data.task, embed_index, str_index, content, "bad")
    
    def update_case(self, data: DataPoint):
        self.update_good_case(data)
        self.update_bad_case(data)
        self.repository.update_corpus()
        
