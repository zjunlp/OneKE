"""
....../OneKE$ python src/webui.py
"""


import gradio as gr
import json
import random
import re
import os

# Set proxy for requests
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

from models import *
from pipeline import Pipeline


examples = [
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "合力治堵!济南交通部门在拥堵路段定点研究交通治理方案",
        "instruction": "请帮我抽取这个新闻事件",
        "constraint": "",
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "NER",
        "mode": "quick",
        "use_file": False,
        "text": "Finally, every other year , ELRA organizes a major conference LREC , the International Language Resources and Evaluation Conference .",
        "instruction": "",
        "constraint": """["algorithm", "conference", "else", "product", "task", "field", "metrics", "organization", "researcher", "program language", "country", "location", "person", "university"]""",
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "RE",
        "mode": "quick",
        "use_file": False,
        "text": "The aid group Doctors Without Borders said that since Saturday , more than 275 wounded people had been admitted and treated at Donka Hospital in the capital of Guinea , Conakry .",
        "instruction": "",
        "constraint": """["nationality", "country capital", "place of death", "children", "location contains", "place of birth", "place lived", "administrative division of country", "country of administrative divisions", "company", "neighborhood of", "company founders"]""",
        "file_path": None,
        "update_case": True,
        "truth": """{"relation_list": [{"head": "Guinea", "tail": "Conakry", "relation": "country capital"}]}""",
    },
    {
        "task": "EE",
        "mode": "standard",
        "use_file": False,
        "text": "The file suggested to the user contains no software related to video streaming and simply carries the malicious payload that later compromises victim \u2019s account and sends out the deceptive messages to all victim \u2019s contacts .",
        "instruction": "",
        "constraint": """{"phishing": ["damage amount", "attack pattern", "tool", "victim", "place", "attacker", "purpose", "trusted entity", "time"], "data breach": ["damage amount", "attack pattern", "number of data", "number of victim", "tool", "compromised data", "victim", "place", "attacker", "purpose", "time"], "ransom": ["damage amount", "attack pattern", "payment method", "tool", "victim", "place", "attacker", "price", "time"], "discover vulnerability": ["vulnerable system", "vulnerability", "vulnerable system owner", "vulnerable system version", "supported platform", "common vulnerabilities and exposures", "capabilities", "time", "discoverer"], "patch vulnerability": ["vulnerable system", "vulnerability", "issues addressed", "vulnerable system version", "releaser", "supported platform", "common vulnerabilities and exposures", "patch number", "time", "patch"]}""",
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Triple",
        "mode": "quick",
        "use_file": True,
        "file_path": "data/input_files/Artificial_Intelligence_Wikipedia.txt",
        "instruction": "",
        "constraint": """[["Person", "Place", "Event", "property"], ["Interpersonal", "Located", "Ownership", "Action"]]""",
        "text": "",
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": True,
        "file_path": "data/input_files/Harry_Potter_Chapter1.pdf",
        "instruction": "Extract main characters and the background setting from this chapter.",
        "constraint": "",
        "text": "",
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": True,
        "file_path": "data/input_files/Tulsi_Gabbard_News.html",
        "instruction": "Extract key information from the given text.",
        "constraint": "",
        "text": "",
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "John Smith, a 45-year-old male, presents with persistent headaches that have lasted for the past 10 days. The headaches are described as moderate and occur primarily in the frontal region, often accompanied by mild nausea. The patient reports no significant medical history except for seasonal allergies, for which he occasionally takes antihistamines. Physical examination reveals a heart rate of 78 beats per minute, blood pressure of 125/80 mmHg, and normal temperature. A neurological examination showed no focal deficits. A CT scan of the head was performed, which revealed no acute abnormalities, and a sinus X-ray suggested mild sinusitis. Based on the clinical presentation and imaging results, the diagnosis is sinusitis, and the patient is advised to take decongestants and rest for recovery.",
        "instruction": "Please extract the key medical information from this case description.",
        "constraint": "",
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "张三，男，60岁，主诉背部酸痛已持续约两周，伴有轻微的头晕。患者有高血压病史，已服用降压药物多年，且控制良好；此外，患者曾在五年前接受过一次胆囊切除手术。体检时，心率为75次/分钟，血压为130/85 mmHg。背部触诊时无明显压痛，但活动时出现轻微不适。胸部X光显示无异常，腰部CT检查提示轻度腰椎退行性变。经医生诊断，患者被认为是由于长时间的不良姿势引起的腰椎退行性病变，建议进行物理治疗，并配合止痛药物。",
        "instruction": "请从这个病例描述中，提取出重要的医疗信息",
        "constraint": "",
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "中国政府近日宣布了一项新的环保政策，旨在减少工业污染，并改善空气质量。此次政策将在全国范围内实施，涉及多个行业，尤其是钢铁和煤炭行业。环保部门负责人表示，这项政策的实施标志着中国环保工作的新阶段，预计将在未来五年内显著改善空气质量。",
        "instruction": "请从这段新闻描述中提取出重要的事件信息，包括事件名称、时间、参与人员、事件目的、实施过程及预期结果。",
        "constraint": "",
        "file_path": None,
        "update_case": False,
        "truth": "",
    }
]


def create_interface():
    with gr.Blocks(title="OneKE Demo", theme=gr.themes.Glass(text_size="lg")) as demo:
        gr.HTML("""
            <div style="text-align:center;">
                <p align="center">
                    <a>
                        <img src="https://raw.githubusercontent.com/zjunlp/OneKE/refs/heads/main/figs/logo.png" width="240"/>
                    </a>
                </p>
                <h1>OneKE: A Dockerized Schema-Guided LLM Agent-based Knowledge Extraction System</h1>
                <p>
                🌐[<a href="http://oneke.openkg.cn/" target="_blank">Home</a>]
                📹[<a href="http://oneke.openkg.cn/demo.mp4" target="_blank">Video</a>]
                📝[<a href="https://arxiv.org/abs/2412.20005v2" target="_blank">Paper</a>]
                💻[<a href="https://github.com/zjunlp/OneKE" target="_blank">Code</a>]
                </p>
            </div>
        """)

        example_button_gr = gr.Button("🎲 Quick Start with an Example 🎲")

        with gr.Row():
            with gr.Column():
                # model_gr = gr.Dropdown(
                #     label="🪄 Select your Model",
                #     choices=["deepseek-chat", "deepseek-reasoner",
                #              "gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o",
                #     ],
                #     value="deepseek-chat",
                # )
                model_gr = gr.Textbox(
                    label="🪄 Enter your Model",
                    placeholder="Supports online-models like gpt-4o-mini, deepseek-chat, etc., while also allowing input of a path to use local models.",
                    value="deepseek-chat",
                )
                api_key_gr = gr.Textbox(
                    label="🔑 Enter your API-Key",
                    placeholder="If using a local-model, this field should be left empty.",
                    value="sk-xxxxx"
                )
                base_url_gr = gr.Textbox(
                    label="🔗 Enter your Base-URL",
                    placeholder="If using the default Base-URL or a local-model, this field should be left empty.",
                    value="Default",
                )
            with gr.Column():
                task_gr = gr.Dropdown(
                    label="🎯 Select your Task",
                    choices=["Base", "NER", "RE", "EE", "Triple"],
                    value="Base",
                )
                mode_gr = gr.Dropdown(
                    label="🧭 Select your Mode",
                    choices=["quick", "standard", "customized"],
                    value="quick",
                )
                schema_agent_gr = gr.Dropdown(choices=["Not Required", "get_default_schema", "get_retrieved_schema", "get_deduced_schema"], value="Not Required", label="🤖 Select your Schema-Agent", visible=False)
                extraction_Agent_gr = gr.Dropdown(choices=["Not Required", "extract_information_direct", "extract_information_with_case"], value="Not Required", label="🤖 Select your Extraction-Agent", visible=False)
                reflection_agent_gr = gr.Dropdown(choices=["Not Required", "reflect_with_case"], value="Not Required", label="🤖 Select your Reflection-Agent", visible=False)

        use_file_gr = gr.Checkbox(label="📂 Use File", value=True)
        file_path_gr = gr.File(label="📖 Upload a File", visible=True)
        text_gr = gr.Textbox(label="📖 Text", lines=5, placeholder="Enter your Text please.", visible=False)
        instruction_gr = gr.Textbox(label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names.", visible=True)
        constraint_gr = gr.Textbox(label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names.", visible=False)

        update_case_gr = gr.Checkbox(label="💰 Update Case", value=False)
        # update_schema_gr = gr.Checkbox(label="📟 Update Schema", value=False)
        truth_gr = gr.Textbox(label="🪙 Truth", lines=2, placeholder="""You can enter the truth you want LLM know, for example: {"relation_list": [{"head": "Guinea", "tail": "Conakry", "relation": "country capital"}]}""", visible=False)
        # selfschema_gr = gr.Textbox(label="📟 Schema", lines=5, placeholder="Enter your New Schema", visible=False,  interactive=True)

        def get_model_category(model_name_or_path):
            if model_name_or_path in ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "o3-mini"]:
                return ChatGPT
            elif model_name_or_path in ["deepseek-chat", "deepseek-reasoner"]:
                return DeepSeek
            elif re.search(r'(?i)llama', model_name_or_path):
                return LLaMA
            elif re.search(r'(?i)qwen', model_name_or_path):
                return Qwen
            elif re.search(r'(?i)minicpm', model_name_or_path):
                return MiniCPM
            elif re.search(r'(?i)chatglm', model_name_or_path):
                return ChatGLM
            else:
                return BaseEngine

        def customized_mode(mode):
            if mode == "customized":
                return gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
            else:
                return gr.update(visible=False, value="Not Required"), gr.update(visible=False, value="Not Required"), gr.update(visible=False, value="Not Required")

        def update_fields(task):
            if task == "Base" or task == "":
                return gr.update(visible=True, label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names."), gr.update(visible=False)
            elif task == "NER":
                return gr.update(visible=False), gr.update(visible=True, label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names.")
            elif task == "RE":
                return gr.update(visible=False), gr.update(visible=True, label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names.")
            elif task == "EE":
                return gr.update(visible=False), gr.update(visible=True, label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names.")
            elif task == "Triple":
                return gr.update(visible=False), gr.update(visible=True, label="🕹️ Instruction", lines=3, placeholder="You can enter any type of information you want to extract here, for example: Please help me extract all the person names.")

        def update_input_fields(use_file):
            if use_file:
                return gr.update(visible=False), gr.update(visible=True)
            else:
                return gr.update(visible=True), gr.update(visible=False)

        def update_case(update_case):
            if update_case:
                return gr.update(visible=True)
            else:
                return gr.update(visible=False)

        # def update_schema(update_schema):
        #     if update_schema:
        #         return gr.update(visible=True)
        #     else:
        #         return gr.update(visible=False)

        def start_with_example():
            example_index = random.randint(-3, len(examples) - 1)
            example_index = max(example_index, 0)
            example = examples[example_index]

            if example_index == 0:
                with open("data/input_files/ChineseNewsExample.json", "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    random_line = random.choice(lines).strip()
                    try:
                        json_data = json.loads(random_line)
                        title = json_data.get("title", "No title found")
                    except json.JSONDecodeError:
                        title = "Error decoding JSON"
                    example["text"] = title

            return (
                gr.update(value=example["task"]),
                gr.update(value=example["mode"]),
                gr.update(value=example["use_file"]),
                gr.update(value=example["file_path"], visible=example["use_file"]),
                gr.update(value=example["text"], visible=not example["use_file"]),
                gr.update(value=example["instruction"], visible=example["task"] == "Base"),
                gr.update(value=example["constraint"], visible=example["task"] in ["NER", "RE", "EE", "Triple"]),
                gr.update(value=example["update_case"]),
                gr.update(value=example["truth"]), # gr.update(value=example["update_schema"]), gr.update(value=example["selfschema"]),
                gr.update(value="Not Required", visible=False),
                gr.update(value="Not Required", visible=False),
                gr.update(value="Not Required", visible=False),
            )

        def submit(model, api_key, base_url, task, mode, instruction, constraint, text, use_file, file_path, update_case, truth, schema_agent, extraction_Agent, reflection_agent):
            try:
                ModelClass = get_model_category(model)
                if base_url == "Default" or base_url == "":
                    if api_key == "":
                        pipeline = Pipeline(ModelClass(model_name_or_path=model))
                    else:
                        pipeline = Pipeline(ModelClass(model_name_or_path=model, api_key=api_key))
                else:
                    if api_key == "":
                        pipeline = Pipeline(ModelClass(model_name_or_path=model, base_url=base_url))
                    else:
                        pipeline = Pipeline(ModelClass(model_name_or_path=model, api_key=api_key, base_url=base_url))

                if task == "Base":
                    instruction = instruction
                    constraint = ""
                else:
                    instruction = ""
                    constraint = constraint
                if use_file:
                    text = ""
                    file_path = file_path
                else:
                    text = text
                    file_path = None
                if not update_case:
                    truth = ""

                agent3 = {}
                if mode == "customized":
                    if schema_agent not in ["", "Not Required"]:
                        agent3["schema_agent"] = schema_agent
                    if extraction_Agent not in ["", "Not Required"]:
                        agent3["extraction_agent"] = extraction_Agent
                    if reflection_agent not in ["", "Not Required"]:
                        agent3["reflection_agent"] = reflection_agent

                # use 'Pipeline'
                _, _, ger_frontend_schema, ger_frontend_res = pipeline.get_extract_result(
                    task=task,
                    text=text,
                    use_file=use_file,
                    file_path=file_path,
                    instruction=instruction,
                    constraint=constraint,
                    mode=mode,
                    three_agents=agent3,
                    isgui=True,
                    update_case=update_case,
                    truth=truth,
                    output_schema="",
                    show_trajectory=False,
                )

                ger_frontend_schema = str(ger_frontend_schema)
                ger_frontend_res = json.dumps(ger_frontend_res, ensure_ascii=False, indent=4) if isinstance(ger_frontend_res, dict) else str(ger_frontend_res)
                return ger_frontend_schema, ger_frontend_res, gr.update(value="", visible=False)

            except Exception as e:
                error_message = f"⚠️ Error:\n {str(e)}"
                return "", "", gr.update(value=error_message, visible=True)

        def clear_all():
            return (
                gr.update(value="Not Required", visible=False),  # sechema_agent
                gr.update(value="Not Required", visible=False),  # extraction_Agent
                gr.update(value="Not Required", visible=False),  # reflection_agent
                gr.update(value="Base"),  # task
                gr.update(value="quick"),  # mode
                gr.update(value="", visible=False),  # instruction
                gr.update(value="", visible=False),  # constraint
                gr.update(value=True),  # use_file
                gr.update(value="", visible=False),  # text
                gr.update(value=None, visible=True),  # file_path
                gr.update(value=False),  # update_case
                gr.update(value="", visible=False), # truth # gr.update(value=False),  # update_schema gr.update(value="", visible=False),  # selfschema
                gr.update(value=""), # py_output_gr
                gr.update(value=""), # json_output_gr
                gr.update(value="", visible=False),  # error_output
            )

        with gr.Row():
            submit_button_gr = gr.Button("Submit", variant="primary", scale=8)
            clear_button = gr.Button("Clear", scale=5)
        gr.HTML("""
		    <div style="width: 100%; text-align: center; font-size: 16px; font-weight: bold; position: relative; margin: 20px 0;">
    			<span style="position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 45%; border-top: 1px solid #ccc;"></span>
	    		<span style="position: relative; z-index: 1; background-color: white; padding: 0 10px;">Output:</span>
			    <span style="position: absolute; right: 0; top: 50%; transform: translateY(-50%); width: 45%; border-top: 1px solid #ccc;"></span>
		    </div>
        """)
        error_output_gr = gr.Textbox(label="😵‍💫 Ops, an Error Occurred", visible=False, interactive=False)
        with gr.Row():
            with gr.Column(scale=1):
                py_output_gr = gr.Code(label="🤔 Generated Schema", language="python", lines=10, interactive=False)
            with gr.Column(scale=1):
                json_output_gr = gr.Code(label="😉 Final Answer", language="json", lines=10, interactive=False)

        task_gr.change(fn=update_fields, inputs=task_gr, outputs=[instruction_gr, constraint_gr])
        mode_gr.change(fn=customized_mode, inputs=mode_gr, outputs=[schema_agent_gr, extraction_Agent_gr, reflection_agent_gr])
        use_file_gr.change(fn=update_input_fields, inputs=use_file_gr, outputs=[text_gr, file_path_gr])
        update_case_gr.change(fn=update_case, inputs=update_case_gr, outputs=[truth_gr])
        # update_schema_gr.change(fn=update_schema, inputs=update_schema_gr, outputs=[selfschema_gr])

        example_button_gr.click(
            fn=start_with_example,
            inputs=[],
            outputs=[
                task_gr,
                mode_gr,
                use_file_gr,
                file_path_gr,
                text_gr,
                instruction_gr,
                constraint_gr,
                update_case_gr,
                truth_gr, # update_schema_gr, selfschema_gr,
                schema_agent_gr,
                extraction_Agent_gr,
                reflection_agent_gr,
            ],
        )
        submit_button_gr.click(
            fn=submit,
            inputs=[
                model_gr,
                api_key_gr,
                base_url_gr,
                task_gr,
                mode_gr,
                instruction_gr,
                constraint_gr,
                text_gr,
                use_file_gr,
                file_path_gr,
                update_case_gr,
                truth_gr, # update_schema_gr, selfschema_gr,
                schema_agent_gr,
                extraction_Agent_gr,
                reflection_agent_gr,
            ],
            outputs=[py_output_gr, json_output_gr, error_output_gr],
            show_progress=True,
        )
        clear_button.click(
            fn=clear_all,
            outputs=[
                schema_agent_gr,
                extraction_Agent_gr,
                reflection_agent_gr,
                task_gr,
                mode_gr,
                instruction_gr,
                constraint_gr,
                use_file_gr,
                text_gr,
                file_path_gr,
                update_case_gr,
                truth_gr, # update_schema_gr, selfschema_gr,
                py_output_gr,
                json_output_gr,
                error_output_gr,
            ],
        )

    return demo


# Launch the front-end interface
if __name__ == "__main__":
    interface = create_interface()
    # interface.launch() # the Gradio defalut URL usually is: 127.0.0.1:7860
    interface.launch(share=True)

