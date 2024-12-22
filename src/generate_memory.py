from typing import Literal
from models import *
from utils import *
from modules import *


class Pipeline:
    def __init__(self, llm: BaseEngine):
        self.llm = llm
        self.case_repo = CaseRepositoryHandler(llm = llm)
        self.schema_agent = SchemaAgent(llm = llm)
        self.extraction_agent = ExtractionAgent(llm = llm, case_repo = self.case_repo)
        self.reflection_agent = ReflectionAgent(llm = llm, case_repo = self.case_repo)        
    
    def __init_method(self, data: DataPoint, process_method):
        default_order = ["schema_agent", "extraction_agent", "reflection_agent"]
        if "schema_agent" not in process_method:
            process_method["schema_agent"] = "get_default_schema"
        if data.task != "Base":
            process_method["schema_agent"] = "get_retrieved_schema"
        if "extraction_agent" not in process_method:
            process_method["extraction_agent"] = "extract_information_direct"
        sorted_process_method = {key: process_method[key] for key in default_order if key in process_method}
        return sorted_process_method
            
    def __init_data(self, data: DataPoint):
        if data.task == "NER":
            data.instruction = config['agent']['default_ner']
            data.output_schema = "EntityList"
        elif data.task == "RE":
            data.instruction = config['agent']['default_re']
            data.output_schema = "RelationList"
        elif data.task == "EE":
            data.instruction = config['agent']['default_ee']
            data.output_schema = "EventList"
        return data
    
    # main entry
    def get_extract_result(self, 
                           task: TaskType,
                           instruction: str = "", 
                           text: str = "", 
                           output_schema: str = "", 
                           constraint: str = "",
                           use_file: bool = False,
                           truth: str = "",
                           mode: str = "quick",
                           update_case: bool = False
                           ):
        
        data = DataPoint(task=task, instruction=instruction, text=text, output_schema=output_schema, constraint=constraint, use_file=use_file, truth=truth)
        data = self.__init_data(data)
        data.instruction = "In the tranquil seaside town, the summer evening cast a golden glow over everything. The townsfolk gathered at the café by the pier, enjoying the sea breeze while eagerly anticipating the annual Ocean Festival's opening ceremony. \nFirst to arrive was Mayor William, dressed in a deep blue suit, holding a roll of his speech. He smiled and greeted the residents, who held deep respect for their community-minded mayor. Beside him trotted Max, his loyal golden retriever, wagging his tail excitedly at every familiar face he saw. \nFollowing closely was Emily, the town’s high school teacher, accompanied by a group of students ready to perform a musical piece they'd rehearsed. One of the girls carried Polly, a vibrant green parrot, on her shoulder. Polly occasionally chimed in with cheerful squawks, adding to the lively atmosphere. \nNot far away, Captain Jack, with his trusty pipe in hand, chatted with old friends about this year's catch. His fleet was the town’s economic backbone, and his seasoned face and towering presence were complemented by the presence of Whiskers, his orange tabby cat, who loved lounging on the dock, attentively watching the gentle waves. \nInside the café, Kate was bustling about, serving guests. As the owner, with her fiery red curls and vivacious spirit, she was the heart of the place. Her friend Susan, an artist living in a tiny cottage nearby, was helping her prepare refreshing beverages. Slinky, Susan's mischievous ferret, darted playfully between the tables, much to the delight of the children present. \nLeaning on the café's railing, a young boy named Tommy watched the sea with wide, gleaming eyes, filled with dreams of the future. By his side sat Daisy, a spirited little dachshund, barking excitedly at the seagulls flying overhead. Tommy's mother, Lucy, stood beside him, smiling softly as she held a seashell he had just found on the beach. \nAmong the crowd, a group of unnamed tourists snapped photos, capturing memories of the charming festival. Street vendors called out, selling their wares—handmade jewelry and sweet confections—as the scent of grilled seafood wafted through the air. \nSuddenly, a burst of laughter erupted—it was James and his band making their grand entrance. Accompanying them was Benny, a friendly border collie who \"performed\" with the band, delighting the crowd with his antics. Set to play a big concert after the opening ceremony, James, the town's star musician, had won the hearts of locals with his soulful tunes. \nAs dusk settled, lights were strung across the streets, casting a magical glow over the town. Mayor William took the stage to deliver his speech, with Max sitting proudly by his side. The festival atmosphere reached its vibrant peak, and in this small town, each person—and animal—carried their own dreams and stories, yet at this moment, they were united by the shared celebration."
        data.chunk_text_list.append("In the tranquil seaside town, the summer evening cast a golden glow over everything. The townsfolk gathered at the café by the pier, enjoying the sea breeze while eagerly anticipating the annual Ocean Festival's opening ceremony. \nFirst to arrive was Mayor William, dressed in a deep blue suit, holding a roll of his speech. He smiled and greeted the residents, who held deep respect for their community-minded mayor. Beside him trotted Max, his loyal golden retriever, wagging his tail excitedly at every familiar face he saw. \nFollowing closely was Emily, the town’s high school teacher, accompanied by a group of students ready to perform a musical piece they'd rehearsed. One of the girls carried Polly, a vibrant green parrot, on her shoulder. Polly occasionally chimed in with cheerful squawks, adding to the lively atmosphere. \nNot far away, Captain Jack, with his trusty pipe in hand, chatted with old friends about this year's catch. His fleet was the town’s economic backbone, and his seasoned face and towering presence were complemented by the presence of Whiskers, his orange tabby cat, who loved lounging on the dock, attentively watching the gentle waves. \nInside the café, Kate was bustling about, serving guests. As the owner, with her fiery red curls and vivacious spirit, she was the heart of the place. Her friend Susan, an artist living in a tiny cottage nearby, was helping her prepare refreshing beverages. Slinky, Susan's mischievous ferret, darted playfully between the tables, much to the delight of the children present. \nLeaning on the café's railing, a young boy named Tommy watched the sea with wide, gleaming eyes, filled with dreams of the future. By his side sat Daisy, a spirited little dachshund, barking excitedly at the seagulls flying overhead. Tommy's mother, Lucy, stood beside him, smiling softly as she held a seashell he had just found on the beach. \nAmong the crowd, a group of unnamed tourists snapped photos, capturing memories of the charming festival. Street vendors called out, selling their wares—handmade jewelry and sweet confections—as the scent of grilled seafood wafted through the air. \nSuddenly, a burst of laughter erupted—it was James and his band making their grand entrance. Accompanying them was Benny, a friendly border collie who \"performed\" with the band, delighting the crowd with his antics. Set to play a big concert after the opening ceremony, James, the town's star musician, had won the hearts of locals with his soulful tunes. \nAs dusk settled, lights were strung across the streets, casting a magical glow over the town. Mayor William took the stage to deliver his speech, with Max sitting proudly by his side. The festival atmosphere reached its vibrant peak, and in this small town, each person—and animal—carried their own dreams and stories, yet at this moment, they were united by the shared celebration.")
        data.distilled_text = "This text is from the field of Slice of Life and represents the genre of Novel."
        data.pred = {
  "characters": [
    {
      "name": "Mayor William",
      "role": "Mayor"
    },
    {
      "name": "Max",
      "role": "Golden Retriever, Mayor William's dog"
    },
    {
      "name": "Emily",
      "role": "High school teacher"
    },
    {
      "name": "Polly",
      "role": "Parrot, accompanying a student"
    },
    {
      "name": "Captain Jack",
      "role": "Captain"
    },
    {
      "name": "Whiskers",
      "role": "Orange tabby cat, Captain Jack's pet"
    },
    {
      "name": "Kate",
      "role": "Café owner"
    },
    {
      "name": "Susan",
      "role": "Artist, Kate's friend"
    },
    {
      "name": "Slinky",
      "role": "Ferret, Susan's pet"
    },
    {
      "name": "Tommy",
      "role": "Young boy"
    },
    {
      "name": "Daisy",
      "role": "Dachshund, Tommy's pet"
    },
    {
      "name": "Lucy",
      "role": "Tommy's mother"
    },
    {
      "name": "James",
      "role": "Musician, band leader"
    },
    {
      "name": "Benny",
      "role": "Border Collie, accompanying James and his band"
    },
    {
      "name": "Unnamed Tourists",
      "role": "Visitors at the festival"
    },
    {
      "name": "Street Vendors",
      "role": "Sellers at the festival"
    }
  ]
}

        data.truth = {
  "characters": [
    {
      "name": "Mayor William",
      "role": "The friendly and respected mayor of the seaside town."
    },
    {
      "name": "Emily",
      "role": "A high school teacher guiding students in a festival performance."
    },
    {
      "name": "Captain Jack",
      "role": "A seasoned sailor whose fleet supports the town."
    },
    {
      "name": "Kate",
      "role": "The welcoming owner of the local café."
    },
    {
      "name": "Susan",
      "role": "An artist known for her ocean-themed paintings."
    },
    {
      "name": "Tommy",
      "role": "A young boy with dreams of the sea."
    },
    {
      "name": "Lucy",
      "role": "Tommy's caring and supportive mother."
    },
    {
      "name": "James",
      "role": "A charismatic musician and band leader."
    }
  ]
}


        # Case Update
        if update_case:
            if (data.truth == ""):
                truth = input("Please enter the correct answer you prefer, or press Enter to accept the current answer: ")
                if truth.strip() == "":
                    data.truth = data.pred
                else:
                    data.truth = extract_json_dict(truth)
            self.case_repo.update_case(data)
        
        # return result
        result = data.pred
        trajectory = data.get_result_trajectory()
        
        return result, trajectory

model = DeepSeek(model_name_or_path="deepseek-chat", api_key="sk-8a1ebfc920a145bea54a5ad6d987dbea")
pipeline = Pipeline(model)
result, trajectory = pipeline.get_extract_result(update_case=True, task="Base")