from typing import List, Optional
from pydantic import BaseModel, Field

# ==================================================================== #  
#                                NER TASK                              #  
# ==================================================================== #  
class Entity(BaseModel):
    type : str = Field("The type or category that the entity belongs to.")
    name : str = Field("The specific name of the entity. ")
    
class EntityList(BaseModel):
    entity_list : List[Entity] = Field("Named entities appearing in the text.")
    
# ==================================================================== #  
#                               RE TASK                                #  
# ==================================================================== #  
class Relation(BaseModel):
    head : str = Field("The starting entity in the relationship.")
    tail : str = Field("The ending entity in the relationship.")
    relation : str = Field("The predicate that defines the relationship between the two entities.")

class RelationList(BaseModel):
    relation_list : List[Relation] = Field("The collection of relationships between various entities.")

# ==================================================================== #  
#                               EE TASK                                #  
# ==================================================================== #  
class Event(BaseModel):
    event_type : str = Field("The type of the event.")
    event_trigger : str = Field("A specific word or phrase that indicates the occurrence of the event.")
    event_argument : dict = Field("The arguments or participants involved in the event.")

class EventList(BaseModel):
    event_list : List[Event] = Field("Events presented in the context.")

# ==================================================================== #  
#                          TEXT DESCRIPTION                            #  
# ==================================================================== #  
class TextDescription(BaseModel):
    field: str = Field("The field of the given text, such as 'Science', 'Literature', 'Business', 'Medicine', 'Entertainment', etc.")
    genre: str = Field("The genre of the given text, such as 'Article', 'Novel', 'Dialog', 'Blog', 'Manual','Expository', 'News Report', 'Research Paper', etc.")
    
# ==================================================================== #  
#                        USER DEFINED SCHEMA                           #  
# ==================================================================== #  

# --------------------------- Research Article ----------------------- #
class MetaData(BaseModel):
    title : str = Field(description="The title of the article")
    authors : List[str] = Field(description="The list of the article's authors")
    abstract: str = Field(description="The article's abstract") 
    key_words: List[str] = Field(description="The key words associated with the article")
    
class Baseline(BaseModel):
    method_name : str = Field(description="The name of the baseline method")
    proposed_solution : str = Field(description="the proposed solution in details")
    performance_metrics : str = Field(description="The performance metrics of the method and comparative analysis")
    
class ExtractionTarget(BaseModel):
    
    key_contributions: List[str] = Field(description="The key contributions of the article")
    limitation_of_sota : str=Field(description="the summary limitation of the existing work")
    proposed_solution : str = Field(description="the proposed solution in details")
    baselines : List[Baseline] = Field(description="The list of baseline methods and their details")
    performance_metrics : str = Field(description="The performance metrics of the method and comparative analysis")
    paper_limitations : str=Field(description="The limitations of the proposed solution of the paper")
    
# --------------------------- News ----------------------- #

class Fact(BaseModel):
    statement: str = Field(description="A factual statement mentioned in the news article")
    source: Optional[str] = Field(description="The source of the fact, if mentioned")
    relevance: Optional[str] = Field(description="The relevance or importance of the fact to the overall article")

class Content(BaseModel):
    headline: str = Field(description="The title or headline of the news article")
    subheading: Optional[str] = Field(description="The subheading or supporting title of the article")
    facts: List[Fact] = Field(description="List of factual statements covered in the article")
    keywords: List[str] = Field(description="List of keywords or topics covered in the article")
    publication_date: str = Field(description="The publication date of the article")
    location: Optional[str] = Field(description="The location relevant to the article")

class NewsReport(BaseModel):
    title: str = Field(description="The title or headline of the news article")
    author: Author = Field(description="The author of the article")
    content: ArticleContent = Field(description="The body and details of the news article")