schema_des_examples = """
Schema: person, time, organization, location
Answer: 
{
  "person": "identified individual",
  "time": "event duration",
  "organization": "goal-oriented group",
  "location": "geographical point"
}

Schema: ["title", "content", "author", "date"]
Answer:
{
  "Title": "document heading",
  "Content": "primary text or info",
  "Author": "creator of content",
  "Date": "associated date"
}
"""

json_schema_examples = """
**Task**: Please extract all economic policies affecting the stock market between 2015 and 2023 and the exact dates of their implementation.
**Text**: This text is from the field of Economics and represents the genre of Article.
...(example text)...
**Output Schema**: 
{
  "economic_policies": [
      {
          "name": null,
          "implementation_date": null
      }
  ]
}

Example2:
**Task**: Tell me the main content of papers related to NLP between 2022 and 2023.
**Text**: This text is from the field of Chemistry and represents the genre of Research Paper.
...(example text)...
**Output Schema**:
{
  "papers": [
      {
          "title": null,
          "content": null
      }
  ]
}

Example3:
**Task**: Extract all the information in the given text.
**Text**: This text is from the field of Political and represents the genre of News Report.
...(example text)...
**Output Schema**:
Answer: 
{
  "news_report": 
    {
      "title": null,
      "summary": null,
      "publication_date": null,
      "keywords": [],
      "events": [
          {
              "name": null,
              "time": null,
              "people_involved": [],
              "cause": null,
              "process": null,
              "result": null
          }
      ],
      quotes: [],
      viewpoints: []
    }
}
"""

code_schema_examples = """
Example1: 
**Task**: Extract all the entities in the given text.
**Text**: 
...(example text)...
**Output Schema**:
```
from typing import List, Optional
from pydantic import BaseModel, Field

class Entity(BaseModel):
    label : str = Field("The type or category of the entity, such as 'Process', 'Technique', 'Data Structure', 'Methodology', 'Person', etc. ")
    name : str = Field("The specific name of the entity. It should represent a single, distinct concept and must not be an empty string. For example, if the entity is a 'Technique', the name could be 'Neural Networks'.")
    
class ExtractionTarget(BaseModel):
    entity_list : List[Entity] = Field("All the entities presented in the context. The entities should encode ONE concept.")
```

Example2: 
**Task**: Extract all the information in the given text.
**Text**: This text is from the field of Political and represents the genre of News Article.
...(example text)...
**Output Schema**:
```
from typing import List, Optional
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="The name of the person")
    role: Optional[str] = Field(description="The role or occupation of the person in the event")

class Event(BaseModel):
    name: str = Field(description="Name of the event")
    time: Optional[str] = Field(description="Time when the event took place")
    people_involved: Optional[List[Person]] = Field(description="People involved in the event")
    cause: Optional[str] = Field(default=None, description="Reason for the event, if applicable")
    process: Optional[str] = Field(description="Details of the event process")
    result: Optional[str] = Field(default=None, description="Result or outcome of the event")

class ExtractionTarget(BaseModel):  
    title: str = Field(description="The title or headline of the news article")
    summary: str = Field(description="A brief summary of the news article")
    publication_date: Optional[str] = Field(description="The publication date of the article")
    keywords: Optional[List[str]] = Field(description="List of keywords or topics covered in the article")
    events: List[Event] = Field(description="Events covered in the article")
    quotes: Optional[List[str]] = Field(default=None, description="Quotes related to the news, if any")
    viewpoints: Optional[List[str]] = Field(default=None, description="Different viewpoints regarding the news")
```

Example3:
**Task**: Extract the key information in the given text.
**Text**: This text is from the field of AI and represents the genre of Academic Article.
...(example text)...
```
from typing import List, Optional
from pydantic import BaseModel, Field

class Baseline(BaseModel):
    method_name : str = Field(description="The name of the baseline method")
    proposed_solution : str = Field(description="the proposed solution in details")
    performance_metrics : str = Field(description="The performance metrics of the method and comparative analysis")
    
class ExtractionTarget(BaseModel):
    title : str = Field(description="The title of the article")
    authors : List[str] = Field(description="The list of the article's authors")
    abstract: str = Field(description="The article's abstract")
    key_contributions: List[str] = Field(description="The key contributions of the article")
    limitation_of_sota : str=Field(description="the summary limitation of the existing work")
    proposed_solution : str = Field(description="the proposed solution in details")
    baselines : List[Baseline] = Field(description="The list of baseline methods and their details")
    performance_metrics : str = Field(description="The performance metrics of the method and comparative analysis")
    paper_limitations : str=Field(description="The limitations of the proposed solution of the paper")
```

"""