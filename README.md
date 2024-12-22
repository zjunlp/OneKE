<h1 align="center"> OneKE </h1>
<h3 align="center"> Dockerized Schema-Guided Knowledge Extraction System </h3>

<p align="center">
  <a href="https://arxiv.org/">📄arXiv</a> •
  <a href="http://oneke.openkg.cn/">🌐Web</a>
</p>


## Table of Contents

- [Table of Contents](#table-of-contents)
- [🌟Overview](#overview)
  - [Input Source Support](#input-source-support)
  - [Extraction Model Support](#extraction-model-support)
  - [Extraction Task Support](#extraction-task-support)
  - [Extraction Method Support](#extraction-method-support)
- [🛠️Installation](#️installation)
  - [Manual Environment Configuration](#manual-environment-configuration)
  - [Building With Docker Images](#building-with-docker-images)
- [🚀Quick-Start](#quick-start)
  - [Start with YAML](#start-with-yaml)
  - [Start with Python](#start-with-python)

---


## 🌟Overview

<img src="./figs/main.png" alt="method" style="zoom: 50%;" />

**OneKE** is a dockerized schema-guided knowledge extraction system, which can extract knowledge from the Web and raw PDF Books, and support various domains (science, news, etc.). Specifically, we design **OneKE** with multiple agents and a configure knowledge base. Different agents perform their respective roles, enabling support for various extraction scenarios. The configure knowledge base facilitates schema configuration, error case debugging and correction, further improving the performance. Empirical evaluations on benchmark datasets demonstrate OneKE’s efficacy, while case studies further elucidate its adaptability to diverse tasks across multiple domains, highlighting its potential for broad applications.

### Input Source Support
You can choose source texts of various lengths and forms for extraction.
  | **Source Format** | **Description** |
  | --- | --- |
  | Plain Text | String form of raw natural language text. |
  | HTML Source | Markup language for structuring web pages. |
  | PDF File | Portable format for fixed-layout documents. |
  | Word File | Microsoft Word document format, with rich text. |
  | TXT File | Basic text format, easily opened and edited. |
  | Json File | Lightweight format for structured data interchange. |

### Extraction Model Support
You can choose from various open-source or proprietary model APIs to perform information extraction tasks.
> Note: For complex open-domain IE tasks, we recommend using powerful models like OpenAI's or or large-scale open-source LLMs.

  | **Model** | **Description** |
  | --- | --- |
  | ***API Support*** |   |
  | OpenAI |  A series of GPT foundation models offered by OpenAI, such as GPT-3.5 and GPT-4-turbo, which are renowned for their outstanding capabilities in natural language processing. |
  | DeepSeek | High-performance LLMs that have demonstrated exceptional capabilities in both English and Chinese benchmarks. |
  | ***Local Deploy***| 
  | LLaMA3 series| Meta's series of large language models, with tens to hundreds of billions of parameters, have shown advanced performance on industry-standard benchmarks. |
  | Qwen2.5 series| LLMs developed by the Qwen team, come in various parameter sizes and exhibit strong capabilities in both English and Chinese. |
  | ChatGLM4-9B | The latest model series by the Zhipu team, which achieve breakthroughs in multiple metrics, excel as bilingual (Chinese-English) chat models. |
  | MiniCPM3-4B | A lightweight language model with 4B parameters,  matches or even surpasses 7B-9B models in most evaluation benchmarks.|

### Extraction Task Support
You can try different types of information extraction tasks within the OneKE framework.
  | **Model** | **Description** |
  | --- | --- |
  | ***Traditional IE*** |   |
  | NER | Named Entity Recognition, identifies and classifies various named entities such as names, locations, and organizations in text. |
  | RE | Relation Extraction, identifies relationships between entities, and typically returns results as entity-relation-entity triples. |
  | EE | Event Extraction, identifies events in text, focusing on event triggers and associated participants, known as event arguments. |
  | ***Open Domain IE***| 
  | Web News Extraction| Involves extracting key entities and events from online news articles to generate structured insights. |
  | Book Knowledged Extraction | Extracts information such as key concepts, themes, and facts from book chapters. |
  | Other | Encompasses information extraction from different types of content, such as social media and research papers, each tailored to the specific context and data type. |

### Extraction Method Support
You can freely combine different extraction methods to complete the information extraction task.
  | **Method** | **Description** |
  | --- | --- |
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
  
## 🛠️Installation
OneKE supports both manual and docker image environment configuration, you can choose the appropriate way to build.
### Manual Environment Configuration
```bash
git clone https://github.com/zjunlp/OneKE.git
cd OneKE
conda create -n oneke python=3.9
conda activate oneke
pip install -r requirements.txt
```
### Building With Docker Images
```
git clone https://github.com/zjunlp/OneKE.git
docker pull zjunlp/oneke:v1
docker run \
  -v ./OneKE:/app/OneKE \
  -v your_local_model_path:/root/model/your_model_name \
  -it oneke /bin/bash

```

## 🚀Quick-Start
### Start with YAML

### Start with Python

<!-- ## ✏️Self-Instruct

We conduct self-instruct on Meta-Agent to acquire a sufficient amount of task data and provide an ample training resource. 

```bash
python Self_Instruct/data_generation.py \
    --source_data Self_Instruct/Meta_sample/Meta_Hotpotqa.json \
    --target_data Self_Instruct/hotpotqa_metaqa.json \
    --dataset_name hotpotqa  \
    --generate_all_num 800 \
    --generate_per_round_num 10 \
    --model_name llama-2-13b-chat \
```

The `source_data` contains data examples from the target task information. The `target_data` consists of data generated through self-instruct. The variable `generate_all_num` represents the total number of generated data instances. In order to improve generation efficiency and avoid duplication, we generate `generate_per_round_num` data instances per round.



## 📝Self-Planning

### Automatic Tool Selection

With the tool library at hand, we ask the Meta-Agent to select applicable tools for each task automatically.

```bash
python Self_Planning/Tool_Selection/tool_selected.py \
    --model_name llama-2-13b-chat \
    --task_name ScienceQA \
    --top_k 40 \
    --top_p 0.75 \
    --max_tokens 1024 \
    --tool_save_path Self_Planning/Tool_Selection/{task_name}_Tools.json
```

The information of the selected tools will be stored in `tool_save_path`.



### Trajectories Synthesis

```bash
python Self_Plan/Traj_Syn/run_task.py \
    --agent_name ZeroshotThink_HotPotQA_run_Agent \
    --llm_name llama-2-13b-chat \
    --max_context_len 4096 \
    --task Hotpotqa \
    --task_path Self_Instruct/hotpotqa_metaqa.json \
    --save_path Self_Plan/Traj_Syn/output/hotpotqa_train_data.jsonl
```

In order to obtain high-quality synthesized trajectories, we filter out all the trajectories with $\texttt{reward}<1$ and collect trajectories with exactly correct answers ($\texttt{reward}=1$) as the training source for self-differentiation. We release the trajectories synthesized by Llama-{13,70}b-chat after filtering in [Google Drive](https://drive.google.com/drive/folders/1Sh6Ksj8T0fT23ePWRf_dDcOTmpZlulr2?usp=sharing) (but you should also run `filter_data.py` for trajectory differentiation).

```bash
python Scripts/filter_data.py \
    --source_path Self_Plan/Traj_Syn/output/hotpotqa_train_data.jsonl \
    --save_path Self_Plan/Traj_Syn/output \
    --task_name HotpotQA \
    --filter_num 200
```



### Self-Differentiation

In order to establish a clear *division-of-labor*, we leverage synthesized planning trajectories to differentiate the Meta-Agent into three sub-agents with distinct functionalities:

- **Plan-Agent** undertakes task decomposition and determines which tool to invoke in each planning loop.
- **Tool-Agent** is responsible for how to invoke the tool by deciding the parameters for the tool invocation.
- **Reflect-Agent** engages in reflection by considering all the historical trajectories and providing a reflection result.

Agent training:

```bash
for agent in plan tool reflect
do
echo "####################"
echo $agent
echo "####################"
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 deepspeed Self_Plan/Train/train_lora.py \
    --model_name_or_path llama-2-13b-chat \
    --lora_r 8 \
    --lora_alpha 16 \
    --lora_dropout 0.05 \
    --data_path Self_Plan/Traj_Syn/output/data_$agent.json \
    --output_dir Self_Plan/Train/lora/HotpotQA/13b-$agent-5-epoch \
    --num_train_epochs 5 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 10000 \
    --save_total_limit 1 \
    --learning_rate 1e-4 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --fp16 True \
    --model_max_length 4096 \
    --gradient_checkpointing True \
    --q_lora False \
    --deepspeed Self_Plan/Train/deepspeed_config_s3.json \
    --resume_from_checkpoint False 
done
```



### Group Planning

After obtaining the task-specific sub-agents, any new question is processed through group planning among the sub-agents to achieve the desired outcome.

```bash
python Self_Planning/Group_Planning/run_eval.py \
    --agent_name ZeroshotThink_HotPotQA_run_Agent \
    --plan_agent plan \
    --tool_agent tool \
    --reflect_agent reflect \
    --max_context_len 4096 \
    --task HotpotQA \
    --task_path Self_Planning/Group_Planning/benchmark_run/data/hotpotqa \
    --save_path Self_Planning/Group_Planning/output/13b
```

We release the trajectories of text sets generated by Llama-{7,13,70}b-chat in [Google Drive](https://drive.google.com/drive/folders/1Sh6Ksj8T0fT23ePWRf_dDcOTmpZlulr2?usp=sharing).

The prompts used in our experiments are in directory [Prompts]https://github.com/zjunlp/AutoAct/tree/main/Prompts.


## 🌻Acknowledgement

Our code of training module is referenced and adapted from [FastChat](https://github.com/lm-sys/FastChat), while the code of inference module is implemented based on [BOLAA](https://github.com/salesforce/BOLAA). Various baseline codes use [ReAct](https://github.com/ysymyth/ReAct), [Reflexion](https://github.com/noahshinn/reflexion), [BOLAA](https://github.com/salesforce/BOLAA), [Chameleon](https://github.com/lupantech/chameleon-llm), [ReWOO](https://github.com/billxbf/ReWOO), [FireAct](https://github.com/anchen1011/FireAct) respectively. We use LangChain with open models via [Fastchat](https://github.com/lm-sys/FastChat/blob/main/docs/langchain_integration.md). Thanks for their great contributions!


## 🚩Citation

Please cite our repository if you use AutoAct in your work. Thanks!

```bibtex
@article{DBLP:journals/corr/abs-2401-05268,
  author       = {Shuofei Qiao and
                  Ningyu Zhang and
                  Runnan Fang and
                  Yujie Luo and
                  Wangchunshu Zhou and
                  Yuchen Eleanor Jiang and
                  Chengfei Lv and
                  Huajun Chen},
  title        = {{AUTOACT:} Automatic Agent Learning from Scratch via Self-Planning},
  journal      = {CoRR},
  volume       = {abs/2401.05268},
  year         = {2024},
  url          = {https://doi.org/10.48550/arXiv.2401.05268},
  doi          = {10.48550/ARXIV.2401.05268},
  eprinttype    = {arXiv},
  eprint       = {2401.05268},
  timestamp    = {Thu, 25 Jan 2024 15:41:08 +0100},
  biburl       = {https://dblp.org/rec/journals/corr/abs-2401-05268.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```



## 🎉Contributors

<a href="https://github.com/zjunlp/AutoAct/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zjunlp/AutoAct" /></a>

We will offer long-term maintenance to fix bugs and solve issues. So if you have any problems, please put issues to us. -->
