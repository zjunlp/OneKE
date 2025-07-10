from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

# ==================================================================== #
#                                NER TASK                              #
# ==================================================================== #
class Entity(BaseModel):
    name : str = Field(description="The specific name of the entity. ")
    type : str = Field(description="The type or category that the entity belongs to.")
class EntityList(BaseModel):
    entity_list : List[Entity] = Field(description="Named entities appearing in the text.")

# ==================================================================== #
#                               RE TASK                                #
# ==================================================================== #
class Relation(BaseModel):
    head : str = Field(description="The starting entity in the relationship.")
    tail : str = Field(description="The ending entity in the relationship.")
    relation : str = Field(description="The predicate that defines the relationship between the two entities.")

class RelationList(BaseModel):
    relation_list : List[Relation] = Field(description="The collection of relationships between various entities.")

# ==================================================================== #
#                               EE TASK                                #
# ==================================================================== #
class Event(BaseModel):
    event_type : str = Field(description="The type of the event.")
    event_trigger : str = Field(description="A specific word or phrase that indicates the occurrence of the event.")
    event_argument : dict = Field(description="The arguments or participants involved in the event.")

class EventList(BaseModel):
    event_list : List[Event] = Field(description="The events presented in the text.")

# ==================================================================== #
#                            Triple TASK                               #
# ==================================================================== #
class Triple(BaseModel):
    head: str = Field(description="The subject or head of the triple.")
    head_type: str = Field(description="The type of the subject entity.")
    relation: str = Field(description="The predicate or relation between the entities.")
    relation_type: str = Field(description="The type of the relation.")
    tail: str = Field(description="The object or tail of the triple.")
    tail_type: str = Field(description="The type of the object entity.")
class TripleList(BaseModel):
    triple_list: List[Triple] = Field(description="The collection of triples and their types presented in the text.")

# ==================================================================== #
#                          TEXT DESCRIPTION                            #
# ==================================================================== #
class TextDescription(BaseModel):
    field: str = Field(description="The field of the given text, such as 'Science', 'Literature', 'Business', 'Medicine', 'Entertainment', etc.")
    genre: str = Field(description="The genre of the given text, such as 'Article', 'Novel', 'Dialog', 'Blog', 'Manual','Expository', 'News Report', 'Research Paper', etc.")

# ==================================================================== #
#                        USER DEFINED SCHEMA                           #
# ==================================================================== #

# --------------------------- Research Paper ----------------------- #
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
class Person(BaseModel):
    name: str = Field(description="The name of the person")
    identity: Optional[str] = Field(description="The occupation, status or characteristics of the person.")
    role: Optional[str] = Field(description="The role or function the person plays in an event.")

class Event(BaseModel):
    name: str = Field(description="Name of the event")
    time: Optional[str] = Field(description="Time when the event took place")
    people_involved: Optional[List[Person]] = Field(description="People involved in the event")
    cause: Optional[str] = Field(default=None, description="Reason for the event, if applicable")
    process: Optional[str] = Field(description="Details of the event process")
    result: Optional[str] = Field(default=None, description="Result or outcome of the event")

class NewsReport(BaseModel):
    title: str = Field(description="The title or headline of the news report")
    summary: str = Field(description="A brief summary of the news report")
    publication_date: Optional[str] = Field(description="The publication date of the report")
    keywords: Optional[List[str]] = Field(description="List of keywords or topics covered in the news report")
    events: List[Event] = Field(description="Events covered in the news report")
    quotes: Optional[dict] = Field(default=None, description="Quotes related to the news, with keys as the citation sources and values as the quoted content. ")
    viewpoints: Optional[List[str]] = Field(default=None, description="Different viewpoints regarding the news")

# --------- You can customize new extraction schemas below -------- #
class ChemicalSubstance(BaseModel):
    name: str = Field(description="Name of the chemical substance")
    formula: str = Field(description="Molecular formula")
    appearance: str = Field(description="Physical appearance")
    uses: List[str] = Field(description="Primary uses")
    hazards: str = Field(description="Hazard classification")

class ChemicalList(BaseModel):
  chemicals: List[ChemicalSubstance] = Field(description="List of chemicals")
