
<p align="center">
  <img src="./figs/logo.png" width="300px">
</p>

<h3 align="center"> A Dockerized Schema-Guided Knowledge Extraction System </h3>

<p align="center">
  <a href="https://arxiv.org/">📄arXiv</a> •
  <a href="http://oneke.openkg.cn/demo.mp4">🌐Video</a>
</p>

## Table of Contents
- [Table of Contents](#table-of-contents)
- [🌟Overview](#overview)
- [🚀Quick Start](#quick-start)
  - [Step1: Environment Setup](#step1-environment-setup)
    - [🔩Manual Environment Configuration](#manual-environment-configuration)
    - [🐳Building With Docker Image](#building-with-docker-image)
  - [Step2: Start with Examples](#step2-start-with-examples)
    - [🖊️Start with YAML](#️start-with-yaml)
    - [🖊️Start with Python](#️start-with-python)
- [🔍Further Usage](#further-usage)
  - [💡Extraction Task Support](#extraction-task-support)
    - [1. Named Entity Recognition](#1-named-entity-recognition)
    - [2. Relation Extraction](#2-relation-extraction)
    - [3. Event Extraction](#3-event-extraction)
    - [4. Open Domain IE](#4-open-domain-ie)
  - [Data Source Support](#data-source-support)
  - [💡Extraction Model Support](#extraction-model-support)
  - [💡Extraction Method Support](#extraction-method-support)
  - [💡Knowledge Base Configuration](#knowledge-base-configuration)
    - [1. Schema Repository](#1-schema-repository)
    - [2. Case Repository](#2-case-repository)
- [🛠️Network Issue Solutions](#️network-issue-solutions)
- [🎉Contributors](#contributors)
- [🌻Acknowledgement](#acknowledgement)

---


## 🌟Overview
**OneKE** is a flexible dockerized system for schema-guided knowledge extraction, capable of extracting information from the web and raw PDF books across multiple domains like science and news. It employs a collaborative multi-agent approach and includes a user-customizable knowledge base to enable tailored extraction. Embark on your information extraction journey with OneKE!

<img src="./figs/main.png" alt="method" style="zoom: 50%;" />

OneKE currently offers the following features:
- [x] Various IE Tasks Support
- [x] Various Data Sources Support
- [x] Various LLMs Support
- [x] Vasious Extraction Method Support
- [x] User-Configurable Knowledge Base


## 🚀Quick Start
We have developed a webpage demo for OneKE with Gradio, click [here](http://120.27.214.45:7876/) try information extraction in an intuitive way.

> Note: The demo only displays OneKE's basic capabilities for effiency. Consider the local deployment steps below for further features.

### Step1: Environment Setup
OneKE supports both manual and docker image environment configuration, choose your preferred method to build.

#### 🔩Manual Environment Configuration
Conda virtual environments offer a light and flexible setup.

**Prerequisites**
- Anaconda Installation
- GPU support (recommended CUDA version: 12.4)

**Configure Steps**
1. Clone the repository:
```bash
git clone https://github.com/zjunlp/OneKE.git
```
1. Enter the working directory, and all subsequent commands should be executed in this directory.
```bash
cd OneKE
```
1. Create a virtual environment using `Anaconda`.
```bash
conda create -n oneke python=3.9
conda activate oneke
```
1. Install all required Python packages.
```bash
pip install -r requirements.txt
# If you encounter network issues, consider setting up a domestic mirror for pip.
```

#### 🐳Building With Docker Image
Docker image provides greater reliability and stability.

**Prerequisites**
- Docker Installation
- NVIDIA Container Toolkit 
- GPU support (recommended CUDA version: 12.4)

**Configure Steps**
1. Clone the repository:
```bash
git clone https://github.com/zjunlp/OneKE.git
```
1. Pull the docker image from the mirror repository.
```bash
docker pull zjunlp/oneke:v1
# If you encounter network issues, consider setting up domestic registry mirrors for docker.
```
3. Launch a container from the image.
```bash
# Use container paths in code and execution
docker run --gpus all \ # start the container
  -v ./OneKE:/app/OneKE \ # map the code to docker container
  -v your_local_model_path:/app/model/your_model_name \ # map the local model to container if necessary
  # map any necessary local files to container here
  -it oneke /bin/bash # launch an interactive bash
```
Upon starting, the container will enter the `/app/OneKE` directory as its working directory.

### Step2: Start with Examples
We offer two quick-start options. Choose your preferred method to swiftly explore OneKE with predefined examples. 

> Note:
> - **Ensure** that your working directory is set to the **`OneKE`** folder, whether in a virtual environment or a docker container. 
> - Refer to [here](#🛠️network-issue-solutions) to resolve the **network issues**. If you have more questions, feel free to open an issue with us.


#### 🖊️Start with YAML
**Step1: Prepare the configuration file**

Several YAML configuration files are available in the `examples/config`. These extraction scenarios cover different extraction data, methods, and models, allowing you to easily explore all the features of OneKE.

***Web News Extraction:***

Here is the example for the web news knowledge extraction scenario, with the source extraction text in `HTML` format:
```yaml
# model configuration
model:
  category: ChatGPT # model category, chosen from ChatGPT, DeepSeek, LLaMA, Qwen, ChatGLM, MiniCPM.
  model_name_or_path: gpt-4o-mini # model name, chosen from the model list of the selected category.
  api_key: your_api_key # your API key for the model with API service. No need for open-source models.
  base_url: https://api.openai.com/v1 # base URL for the API service. No need for open-source models.

# extraction configuration
extraction:             
  task: Base # task type, chosen from Base, NER, RE, EE.
  instruction: Extract key information from the given text. # description for the task. No need for NER, RE, EE task.
  use_file: true # whether to use a file for the input text. Default set to false.
  file_path: ./data/input_files/Tulsi_Gabbard_News.html # path to the input file. No need if use_file is set to false.
  output_schema: NewsReport # output schema for the extraction task. Selected the from schema repository.
  mode: customized # extraction mode, chosen from quick, detailed, customized. Default set to quick. See src/config.yaml for more details.
  update_case: false # whether to update the case repository. Default set to false.
```

***Book News Extraction:***

Here is the example for the book news extraction scenario, with the source extraction text in `PDF` format:
```yaml
model:
  category: ChatGPT # model category, chosen from ChatGPT, DeepSeek, LLaMA, Qwen, ChatGLM, MiniCPM.
  model_name_or_path: gpt-4o-mini # model name, chosen from the model list of the selected category.
  api_key: your_api_key # your API key for the model with API service. No need for open-source models.
  base_url: https://api.openai.com/v1 # base URL for the API service. No need for open-source models.

extraction:             
  task: Base # task type, chosen from Base, NER, RE, EE.
  instruction: Extract key information from the given text. # description for the task. No need for NER, RE, EE task.
  use_file: true # whether to use a file for the input text. Default set to false.
  file_path: ./data/input_files/Tulsi_Gabbard_News.html # path to the input file. No need if use_file is set to false.
  output_schema: NewsReport # output schema for the extraction task. Selected the from schema repository.
  mode: customized # extraction mode, chosen from quick, detailed, customized. Default set to quick. See src/config.yaml for more details.
  update_case: false # whether to update the case repository. Default set to false.
```

The `model` section contains information about the extraction model, while the `extraction` section configures the settings for the extraction process.

You can choose an existing configuration file or customize the extraction settings as you wish. Note that when using an API service like ChatGPT and DeepSeek, please **set your API key**.

**Step2: Run the shell script**

Specify the configuration file path and run the code to start the extraction process.
```bash
config_file=your_yaml_file_path # configuration file path, use the container path if inside a container
python src/run.py --config $config_file # executed in the OneKE directory
```

#### 🖊️Start with Python
You can also try OneKE by directly running the `example.py` file located in the `example` directory. Specifically, execute the following commands:
```bash
python examples/example.py
```

This will complete a basic NER task, with the extraction results printed upon completion. You can further modify the code in `example.py` to suit your extraction task setting or to access detailed extraction trajectory.

***Named Entity Extraction:***

Specifically, we present a NER case in the `example.py` file:
```python
import sys
sys.path.append("./src")
from models import *
from pipeline import *
import json

# model configuration
model = ChatGPT(model_name_or_path="gpt-4o-mini", api_key="your_api_key")
pipeline = Pipeline(model)

# extraction configuration
Task = "NER"
Text = "Finally , every other year , ELRA organizes a major conference LREC , the International Language Resources and Evaluation Conference ."
Constraint = nationality, country capital, place of death, children, location contains, place of birth, place lived, administrative division of country, country of administrative divisions, company, neighborhood of, company founders

# get extraction result
result, trajectory = pipeline.get_extract_result(task=Task, text=Text, constraint=Constraint)
print("Trajectory:", json.dumps(trajectory, indent=4))
```
First, select an appropriate extraction model, then complete the configuration of extraction parameters (such as extraction task, extraction text, etc.). Finally, call the `get_extract_result` function of the `Pipeline` class to perform information extraction and obtain the final results.

## 🔍Further Usage
### 💡Extraction Task Support
You can try different types of information extraction tasks within the OneKE framework.
  | **Task** | **Description** |
  | :---: | :---: |
  | ***Traditional IE*** |   |
  | NER | Named Entity Recognition, identifies and classifies various named entities such as names, locations, and organizations in text. |
  | RE | Relation Extraction, identifies relationships between entities, and typically returns results as entity-relation-entity triples. |
  | EE | Event Extraction, identifies events in text, focusing on event triggers and associated participants, known as event arguments. |
  | ***Open Domain IE***| 
  | Web News Extraction| Involves extracting key entities and events from online news articles to generate structured insights. |
  | Book Knowledged Extraction | Extracts information such as key concepts, themes, and facts from book chapters. |
  | Other | Encompasses information extraction from different types of content, such as social media and research papers, each tailored to the specific context and data type. |

In subsequent code processing, we categorize tasks into four types: `NER` for Named Entity Recognition, `RE` for Relation Extraction, `EE` for Event Extraction, and `Base` for any other user-defined open-domain extraction tasks.


#### 1. Named Entity Recognition
Named entity recognition seeks to locate and classify named entities mentioned in unstructured text into pre-defined entity types such as person names, organizations, locations, organizations, etc.

Refer to the case defined in `examples/config/NER.yaml` as an example:
| Text | Entity Types |
| --- |--- |
| Finally, every other year, ELRA organizes a major conference LREC, the International Language Resources and Evaluation Conference. | Algorithm, Conference, Else, Product, Task, Field, Metrics, Organization, Researcher, Program Language, Country, Location, Person, University |

In this task setting, `Text` represents the text to be extracted, while `Entity Types` denote the constraint on the types of entities to be extracted. Accordingly, we set the `text` and `constraint` attributes in the YAML file to their respective values.

Next, run the following code to complete this NER task:
( Refer to [here](#🛠️network-issue-solutions) for any network issues. )
```bash
config_file=./examples/config/NER.yaml 
python src/run.py --config $config_file 
```

The final extraction result should be:
| Text | Conference |
| --- | --- |
| Finally, every other year, ELRA organizes a major conference LREC, the International Language Resources and Evaluation Conference. | ELRA, conference, International Language Resources and Evaluation Conference | 
> Note: The actual extraction results may not exactly match this due to LLM randomness.

The result indicates that, given the text and entity type constraint, entities of type `conference` have been extracted: `ELRA`, `conference`, `International Language Resources and Evaluation Conference`.

You can either specify entity type constraints or omit them. Without constraints, OneKE will extract all entities from the sentence.


#### 2. Relation Extraction
Relationship extraction is the task of extracting semantic relations between entities from a unstructured text.

Refer to the case defined in `examples/config/RE.yaml` as an example:
| Text | Relation Types |
| --- |--- |
|  The aid group Doctors Without Borders said that since Saturday , more than 275 wounded people had been admitted and treated at Donka Hospital in the capital of Guinea , Conakry . | Nationality, Country Capital, Place of Death, Children, Location Contains, Place of Birth, Place Lived, Administrative Division of Country, Country of Administrative Divisions, Company, Neighborhood of, Company Founders |

In this task setting, `Text` represents the text to be extracted, while `Relation Types` denote the constraint on the types of relations of entities to be extracted. Accordingly, we set the `text` and `constraint` attributes in the YAML file to their respective values.

Next, run the following code to complete this NER task:
( Refer to [here](#🛠️network-issue-solutions) for any network issues. )
```bash
config_file=./examples/config/RE.yaml 
python src/run.py --config $config_file 
```

The final extraction result should be:

| Text | Head Entity | Tail Entity | Relationship |
| --- | --- | --- | --- |
| The aid group Doctors Without Borders said that since Saturday , more than 275 wounded people had been admitted and treated at Donka Hospital in the capital of Guinea , Conakry . | Guinea | Conakry | Country-Capital |
> Note: The actual extraction results may not exactly match this due to LLM randomness.

The result indicates that, the relation `Country-Capital` is extracted from the given text based on the relation list, accompanied by the corresponding head entity `Guinea` and tail entity `Conakry`, which denotes that `Conakry is the capital of Guinea`.

You can either specify relation type constraints or omit them. Without constraints, OneKE will extract all relation triples from the sentence.


#### 3. Event Extraction
Event extraction is the task to extract event type, event trigger words, and event arguments from a unstructed text, which is a more complex IE task compared to the first two.

Refer to the case defined in `examples/configEE.yaml` as an example:
The extraction text is :
```
UConn Health , an academic medical center , says in a media statement that it identified approximately 326,000 potentially impacted individuals whose personal information was contained in the compromised email accounts.
```
while the event type constraint is formatted as follows:
| Event Type | Event Argument |
| --- | --- |
| phishing | damage amount, attack pattern, tool, victim, place, attacker, purpose, trusted entity, time |
| data breach | damage amount, attack pattern, number of data, number of victim, tool, compromised data, victim, place, attacker, purpose, time |
| ransom | damage amount, attack pattern, payment method, tool, victim, place, attacker, price, time |
| discover vulnerability | vulnerable system, vulnerability, vulnerable system owner, vulnerable system version, supported platform, common vulnerabilities and exposures, capabilities, time, discoverer |
| patch vulnerability | vulnerable system, vulnerability, issues addressed, vulnerable system version, releaser, supported platform, common vulnerabilities and exposures, patch number, time, patch |

Each event type has its own corresponding event arguments.

Next, run the following code to complete this NER task:
( Refer to [here](#🛠️network-issue-solutions) for any network issues. )
```bash
config_file=./examples/config/EE.yaml 
python src/run.py --config $config_file 
```

The final extraction result should be:

<table>
  <tr>
    <th>Text</th>
    <th>Event Type</th>
    <th>Event Trigger</th>
    <th>Argument</th>
    <th>Role</th>
  </tr>
  <tr>
    <td rowspan="4">UConn Health , an academic medical center , says in a media statement that it identified approximately 326,000 potentially impacted individuals whose personal information was contained in the compromised email accounts.</td>
    <td rowspan="4">data breach</td>
    <td rowspan="4">compromised</td>
    <td>email accounts</td>
    <td>compromised data</td>
  </tr>
  <tr>
    <td>326,000</td>
    <td>number of victim</td>
  </tr>
  <tr>
    <td>individuals</td>
    <td>victim</td>
  </tr>
  <tr>
    <td>personal information</td>
    <td>compromised data</td>
  </tr>
</table>

> Note: The actual extraction results may not exactly match this due to LLM randomness.

The extraction results show that the `data breach` event is identified using the trigger `compromised`, and the specific contents of different event arguments such as `compromised data` and `victim` have also been extracted.

You can either specify event constraints or omit them. Without constraints, OneKE will extract all events from the sentence.

#### 4. Open Domain IE
This type of task is represented as `Base` in the code, signifying any other user-defined open-domain extraction tasks.

We refer to the [example](#step1-prepare-the-configuration-file) above for guidance. 

In the context of customized **Web News Extraction**, we first set the extraction instruction to `Extract key information from the given text`, and provide the file path to extract content from the file. We specify the output schema from the schema repository as the predefined `NewsReport`, and then proceed with the extraction.

Next, run the following code to complete this task:
( Refer to [here](#🛠️network-issue-solutions) for any network issues. )
```bash
config_file=./examples/config/NewsExtraction.yaml 
python src/run.py --config $config_file 
```

Here is an excerpt of the extracted content:
| **Title**                        | Meet Trump's pick for director of national intelligence |
|----------------------------------|--------------------------------------------------------------------------------|
| **Summary**                      | Tulsi Gabbard, chosen by President-elect Donald Trump for director of national intelligence, faces a Senate confirmation challenge due to her lack of experience and controversial views. Accusations include promoting an anti-American agenda and having troubling ties with U.S. adversaries. |
| **Publication Date**             | 2024-12-04T17:06:00Z                                                           |
| **Keywords**                     | Tulsi Gabbard; director of national intelligence; Donald Trump; Senate confirmation; intelligence agencies |
| **Events**                       | Tulsi Gabbard's nomination leads to a Senate confirmation battle due to controversies.                           |
| **People Involved**              | Tulsi Gabbard: Nominee for director of national intelligence; Donald Trump: President-elect; Tammy Duckworth: Democratic Senator; Olivia Troye: Former Trump administration national security official |
| **Quotes**                       | "The U.S. intelligence community has identified her as having troubling relationships with America’s foes."; "If Gabbard is confirmed, America’s allies may not share as much information with the U.S."  |
| **Viewpoints**                   | Gabbard's nomination is considered alarming and dangerous for U.S. national security; Her anti-war stance and criticism of military interventions draw both support and criticism. |

> Note: The actual extraction results may not exactly match this due to LLM randomness.

In contrast to eariler tasks, the `Base-type` Task requires you to provide an explicit `Instruction` that clearly defines your extraction task, while not allowing the setting of `constraint` values.



### Data Source Support
You can choose source texts of various lengths and forms for extraction.
  | **Source Format** | **Description** |
  | :---: | :---: |
  | Plain Text | String form of raw natural language text. |
  | HTML Source | Markup language for structuring web pages. |
  | PDF File | Portable format for fixed-layout documents. |
  | Word File | Microsoft Word document format, with rich text. |
  | TXT File | Basic text format, easily opened and edited. |
  | Json File | Lightweight format for structured data interchange. |

In practice, you can use the YAML file configuration to handle different types of text input:
- **Plain Text**:  Set `use_file` to `false` and enter the text to be extracted in the `text` field.
  For example:
  ```yaml
  use_file: false
  text: Finally , every other year , ELRA organizes a major conference LREC , the International Language Resources and Evaluation Conference .
  ```
- **File Content**: Set `use_file` to `true` and specify the file path in `file_path` for the text to be extracted.
  For example:
  ```yaml
  use_file: true
  file_path: ./data/input_files/Tulsi_Gabbard_News.html
  ```


### 💡Extraction Model Support
You can choose from various open-source or proprietary model APIs to perform information extraction tasks.
> Note: For complex IE tasks, we recommend using powerful models like **OpenAI**'s or or **large-scale** open-source LLMs.

  | **Model** | **Description** |
  | :---: | :---: |
  | ***API Service*** |   |
  | OpenAI |  A series of GPT foundation models offered by OpenAI, such as GPT-3.5 and GPT-4-turbo, which are renowned for their outstanding capabilities in natural language processing. |
  | DeepSeek | High-performance LLMs that have demonstrated exceptional capabilities in both English and Chinese benchmarks. |
  | ***Local Deploy***| 
  | LLaMA3 series| Meta's series of large language models, with tens to hundreds of billions of parameters, have shown advanced performance on industry-standard benchmarks. |
  | Qwen2.5 series| LLMs developed by the Qwen team, come in various parameter sizes and exhibit strong capabilities in both English and Chinese. |
  | ChatGLM4-9B | The latest model series by the Zhipu team, which achieve breakthroughs in multiple metrics, excel as bilingual (Chinese-English) chat models. |
  | MiniCPM3-4B | A lightweight language model with 4B parameters,  matches or even surpasses 7B-9B models in most evaluation benchmarks.|

In practice, you can use the YAML file configuration to employ various LLMs:
- **API Service**:  Set the `model_name_or_path` to the available model name provided by the company, and enter your `api_key` as well as the `base_url`.
  For exmaple:
  ```yaml
  model:
    category: ChatGPT # model category, chosen from ChatGPT, DeepSeek, LLaMA, Qwen, ChatGLM, MiniCPM.
    model_name_or_path: gpt-4o-mini # model name, chosen from the model list of the selected category.
    api_key: your_api_key # your API key for the model with API service. No need for open-source models.
    base_url: https://api.openai.com/v1 # base URL for the API service. No need for open-source models.
  ```
- **Local Deploy**: Set the `model_name_or_pat` to either the model name on Hugging Face or the path to the local model.
  For exmaple:
  ```yaml
  model:
    category: LLaMA # model category, chosen from ChatGPT, DeepSeek, LLaMA, Qwen, ChatGLM, MiniCPM.
    model_name_or_path: meta-llama/Meta-Llama-3-8B-Instruct # model name to download from huggingface or use the local model path.
  ```
Note that the category of model **must** be chosen from ChatGPT, DeepSeek, LLaMA, Qwen, ChatGLM, MiniCPM.

### 💡Extraction Method Support
You can freely combine different extraction methods to complete the information extraction task.
  | **Method** | **Description** |
  | :---: | :---: |
  | ***Schema Agent*** |   |
  | Default Schema | Use the default JSON output format. |
  | Predefined Schema | Utilize the predefined output schema retrieved from the knowledge base. |
  | Self Schema Deduction | Generate the output schema by inferring from the task description and the source text. |
  | ***Extraction Agent***| 
  | Direct IE | Directly extract information from the given text based on the task description. |
  | Case Retrieval | Retrieve similar good cases from the knowledge base to aid in the extraction. |
  | ***Reflection Agent***| 
  | No Reflection| Directly return the extraction results. |
  | Case Reflection  | Use the self-consistency approach, and if inconsistencies appear, reflect on the original answer by retrieving similar bad cases from the knowledge base. |

The configuration for detail extraction methods and mode information can be found in `src/config.yaml`. You can customize the extraction methods by modifying the `customized` within this file and set the `mode` to customize in an external configuration file.

For example, first configure the `src/config.yaml` as follows:
```yaml
# src/config.yaml
customized:
    schema_agent:  get_deduced_schema
    extraction_agent: extract_information_direct
    reflection_agent: reflect_with_case
```
Then, set the `mode` of your custom extraction task in `examples/customized.yaml` to `customized`:

```yaml
# examples/customized.yaml
mode: customized
```
This allows you to experience the customized extraction methods.

> Tips: 
> - For longer text extraction tasks, we recommend using the `direct mode` to avoid issues like attention dispersion and increased processing time. 
> - For shorter tasks requiring high accuracy, you can try the `standard mode` to ensure precision.


### 💡Knowledge Base Configuration
#### 1. Schema Repository
You can view the predefined schemas within the `src/modules/knowledge_base/schema_repository.py` file. The Schema Repository is designed to be easily extendable. You just need to define your output schema in the form of a pydantic class following the format defined in the file, and it can be directly used in subsequent extractions.

For example, add a new schema in the schema repository:
```python
# src/modules/knowledge_base/schema_repository.py
class ChemicalSubstance(BaseModel):
    name: str = Field(description="Name of the chemical substance")
    formula: str = Field(description="Molecular formula")
    appearance: str = Field(description="Physical appearance")
    uses: List[str] = Field(description="Primary uses")
    hazards: str = Field(description="Hazard classification")

class ChemicalList(BaseModel)
  chemicals: List[str] = Field(description="List of chemicals")
```

Then, set the method for `schema_agent` under `customized` to `get_retrieved_schema` in `src/config.yaml`. Finally, set the `mode` to `customized` in the external configuration file to enable custom schema extraction. 

In this example, the extraction results will be a list of **chemical substances** that strictly adhere to the defined schema, ensuring a high level of accuracy and flexibility in the extraction results.

Note that the names of newly created objects **should not conflict with** existing ones.

#### 2. Case Repository
You can directly view the case storage in the `src/modules/knowledge_base/case_repository.json` file, but we do not recommend modifying it directly. 

The Case Repository is automatically updated with each extraction process once setting `update_repository` to `True` in the configuration file. 

When updating the Case Repository, you must provide external feedback to generate case information, either by including truth answer in the configuration file or during the extraction process.

Here is an example:
```yaml
  # examples/config/RE.yaml
  truth: {"relation_list": [{"head": "Guinea", "tail": "Conakry", "relation": "country capital"}]} # Truth data for the relation 
  update_case: true 
```

After extraction, OneKE compares results with the truth answer, generates analysis, and finally stores the case in the repository.


## 🛠️Network Issue Solutions
Here are some network issues you might encounter and the corresponding solutions.

- Pip Installation Failure: Use mirror websites, run the command as `pip install -i [mirror-source] ...`.
- Docker Image Pull Failure: Configure the docker daemon to add repository mirrors.
- Nltk Download Failure: Manually download the `nltk` package and place it in the proper directory.
- Model Dowload Failure: Use the `Hugging Face` mirror site or `ModelScope` to download model, and specify the local path to the model when using it. 
    > Note: We use `all-MiniLM-L6-v2` model by default for case matching, so it needs to be downloaded during execution. If network issues occur, manually download the model, and update the `embedding_model` to its local path in the `/src/config.yaml` file.


## 🎉Contributors

<a href="https://github.com/zjunlp/OneKE/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zjunlp/OneKE" /></a>

We deeply appreciate the collaborative efforts of everyone involved. We will continue to enhance and maintain this repository over the long term. If you encounter any issues, feel free to submit them to us!


## 🌻Acknowledgement
We reference [itext2kg](https://github.com/AuvaLab/itext2kg) to aid in building the schema repository and utilize tools from [LangChain](https://www.langchain.com/) for file parsing. The experimental datasets we use are curated from the [IEPile](https://huggingface.co/datasets/zjunlp/iepile) repository. We appreciate their valuable contributions!
