"""
....../OneKE$ python src/webui.py
"""


import streamlit as st
import json
import random
import re
import os
from io import StringIO
from models import *
from pipeline import Pipeline
import chardet
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


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


# model category
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


# read file
def read_file_content(raw_data):
    result = chardet.detect(raw_data)
    encoding = result['encoding'] or 'utf-8'

    try:
        return raw_data.decode(encoding)
    except UnicodeDecodeError:
        # try common encoding
        for enc in ['gbk', 'gb2312', 'gb18030']:
            try:
                return raw_data.decode(enc)
            except:
                pass
        return raw_data.decode('utf-8', errors='ignore')

@st.cache_data  #add cache
def create_graph(triples_data):
    # create NetworkX graph
    G = nx.DiGraph()

    # node colors map
    color_map = {
        "Event": "#FF9999",
        "property": "#99CCFF",
        "Action": "#99FF99",
        "default": "#CCCCCC"
    }

    # deal with each triple
    for triple in triples_data["triple_list"]:
        head = triple.get("head", "")
        tail = triple.get("tail", "")
        relation = triple.get("relation", "")

        if not head or not tail or not relation:
            continue

        head_type = triple.get("head_type", "default")
        tail_type = triple.get("tail_type", "default")

        # add node
        G.add_node(head, type=head_type, color=color_map.get(head_type, "#CCCCCC"))
        G.add_node(tail, type=tail_type, color=color_map.get(tail_type, "#CCCCCC"))

        # add edge
        G.add_edge(head, tail, label=relation)
    return G

def visualize_knowledge_graph(triples_data):
    # validate data structure(triple)
    if not triples_data or not isinstance(triples_data, dict):
        st.warning("Invalid triples data format")
        return

    if "triple_list" not in triples_data or not isinstance(triples_data["triple_list"], list):
        st.warning("No valid triples data to visualize (missing 'triple_list' or not a list)")
        return

    if len(triples_data["triple_list"]) == 0:
        st.info("Empty triples list - no visualization available")
        return

    try:
        # force-directed layout for position of node
        G = create_graph(triples_data)
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

        # create Plotly graph
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')


        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        node_full_names = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_full_names.append(node)
            node_text.append(
                f"{node[:15]}{'...' if len(node) > 15 else ''}<br>Type: {G.nodes[node].get('type', 'default')}")
            node_colors.append(G.nodes[node]['color'])
            node_sizes.append(20 + 0.3 * len(node))

        # create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[node[:10] + (node[10:] and '..') for node in node_full_names],
            textposition="middle center",
            marker=dict(
                color=node_colors,
                size=node_sizes,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            hoverinfo='text',
            hovertext=node_text,
            customdata=node_full_names,
            name="Nodes"
        )

        # create relation label
        label_x = []
        label_y = []
        label_text = []

        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            label_x.append(x0 * 0.4 + x1 * 0.6)
            label_y.append(y0 * 0.4 + y1 * 0.6)
            label_text.append(edge[2]['label'])

        label_trace = go.Scatter(
            x=label_x, y=label_y,
            mode='text',
            text=label_text,
            textposition="middle center",
            hoverinfo='none',
            textfont=dict(size=10, color='black')
        )

        # create figure
        fig = go.Figure(data=[edge_trace, node_trace, label_trace],
                        layout=go.Layout(
                            title='Knowledge Graph',
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=600,
                            clickmode='event+select'
                        ))

        # table for selecting node
        SELECTBOX_KEY = "kg_node_selector"
        node_list = list(G.nodes())

        if not node_list:
            st.info("No nodes available")
        else:
            if SELECTBOX_KEY not in st.session_state or st.session_state[SELECTBOX_KEY] not in node_list:
                st.session_state[SELECTBOX_KEY] = node_list[0]

            # make layout fixed
            fig.update_layout(uirevision="fixed_layout")

            st.plotly_chart(
                fig,
                use_container_width=True,
                key="fixed_kg_chart"  # key to fix layout
            )

            #create select-node box
            selected_node = st.selectbox(
                "Select a node to view details",
                options=node_list,
                index=node_list.index(st.session_state[SELECTBOX_KEY]),
                key=SELECTBOX_KEY
            )

            if selected_node:
                node_info = G.nodes[selected_node]
                st.markdown(f"**Full Name:** {selected_node}")
                st.markdown(f"**Type:** {node_info.get('type', 'default')}")

                st.markdown("**Relationships:**")
                for neighbor in G.neighbors(selected_node):
                    relation = G.edges[selected_node, neighbor]['label']
                    st.markdown(f"- {relation} ➔ **{neighbor}**")

                for predecessor in G.predecessors(selected_node):
                    if predecessor != selected_node:  # avoid circle
                        relation = G.edges[predecessor, selected_node]['label']
                        st.markdown(f"- {relation} ← **{predecessor}**")

    except Exception as e:
        st.error(f"Visualization error: {str(e)}")


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    st.markdown(
        """
        <div style="text-align:center;">
            <p align="center">
                <a>
                    <img src="https://raw.githubusercontent.com/zjunlp/OneKE/refs/heads/main/figs/logo.png" width="180"/>
                </a>
            </p>
            <h1 style="font-size: 24px;">OneKE: A Dockerized Schema-Guided LLM Agent-based Knowledge Extraction System</h1>
            <p>
            🌐[<a href="http://oneke.openkg.cn/" target="_blank">Home</a>]
            📹[<a href="http://oneke.openkg.cn/demo.mp4" target="_blank">Video</a>]
            📝[<a href="https://arxiv.org/abs/2412.20005v2" target="_blank">Paper</a>]
            💻[<a href="https://github.com/zjunlp/OneKE" target="_blank">Code</a>]
            </p>
        </div>
    """,
        unsafe_allow_html=True
    )

    # initialize session_state
    if 'example_index' not in st.session_state:
        st.session_state.example_index = -1
    if 'submit_pressed' not in st.session_state:
        st.session_state.submit_pressed = False
    if 'file_content' not in st.session_state:
        st.session_state.file_content = ""

    col1, col2, col3 = st.columns([1.8, 3, 1])
    with col2:
        # example button
        if st.button("🎲 Quick Start with an Example 🎲"):
            st.session_state.example_index = random.randint(0, len(examples) - 1)
            st.session_state.submit_pressed = False
            st.rerun()

    # load data from example
    if st.session_state.example_index >= 0:
        example = examples[st.session_state.example_index]

        # use random news example
        if st.session_state.example_index == 0:
            try:
                with open("data/input_files/ChineseNewsExample.json", "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    random_line = random.choice(lines).strip()
                    json_data = json.loads(random_line)
                    example["text"] = json_data.get("title", "No title found")
            except:
                pass

    # construct state for neo4j
    if 'construct' not in st.session_state:
        st.session_state.construct = {
            'database':'Neo4j',
            'url': '',
            'username': '',
            'password': ''
        }

    # model configuration
    st.subheader("Model Configuration")
    with st.expander("Model Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            model = st.text_input(
                "🪄 Enter your Model",
                "deepseek-chat" if st.session_state.example_index < 0
                else examples[st.session_state.example_index].get("model", "deepseek-chat"),
                help="Supports online-models like gpt-4o-mini, deepseek-chat, etc., while also allowing input of a path to use local models."
            )

            api_key = st.text_input(
                "🔑 Enter your API-Key",
                value="sk-xxxxx",
                help="If using a local-model, this field should be left empty."
            )

            base_url = st.text_input(
                "🔗 Enter your Base-URL",
                help="If using the default Base-URL or a local-model, this field should be left empty."
            )

        with col2:
            task = st.selectbox(
                "🎯 Select your Task",
                ["Base", "NER", "RE", "EE", "Triple"],
                index=0 if st.session_state.example_index < 0
                else ["Base", "NER", "RE", "EE", "Triple"].index(
                    examples[st.session_state.example_index].get("task", "Base"))
            )

            mode = st.selectbox(
                "🧭 Select your Mode",
                ["quick", "standard", "customized"],
                index=0 if st.session_state.example_index < 0
                else ["quick", "standard", "customized"].index(
                    examples[st.session_state.example_index].get("mode", "quick"))
            )

            if mode == "customized":
                schema_agent = st.selectbox(
                    "🤖 Select your Schema-Agent",
                    ["Not Required", "get_default_schema", "get_retrieved_schema", "get_deduced_schema"]
                )
                extraction_agent = st.selectbox(
                    "🤖 Select your Extraction-Agent",
                    ["Not Required", "extract_information_direct", "extract_information_with_case"]
                )
                reflection_agent = st.selectbox(
                    "🤖 Select your Reflection-Agent",
                    ["Not Required", "reflect_with_case"]
                )
            else:
                schema_agent = extraction_agent = reflection_agent = "Not Required"


    #show construct for Triple task
    if task == "Triple":
        iskg = st.checkbox(
            "🧩 Construct Knowledge Graph",
            value=st.session_state.get('iskg', False),
            help="Construct knowledge graph in Neo4j database."
        )
        if iskg:
            with st.expander("🧩 Neo4j Knowledge Graph Configuration", expanded=True):
                neo_col1, neo_col2 = st.columns(2)

                with neo_col1:
                    st.session_state.construct['url'] = st.text_input(
                        "Neo4j URL",
                        value="neo4j+s://your-instance.databases.neo4j.io" if st.session_state.construct['url'] == ''
                        else st.session_state.construct['url'],
                        help="Your Neo4j connection URL"
                    )

                    st.session_state.construct['username'] = st.text_input(
                        "Username",
                        value="neo4j" if st.session_state.construct['username'] == ''
                        else st.session_state.construct['username']
                    )

                with neo_col2:
                    st.session_state.construct['password'] = st.text_input(
                        "Password",
                        value="your-password" if st.session_state.construct['password'] == ''
                        else st.session_state.construct['password'],
                        type="password"
                    )

                    st.markdown("###")
                    test_button = st.button("🔗 Test Neo4j Connection", key="test_neo4j")
                    if test_button:
                        try:
                            driver = GraphDatabase.driver(
                                st.session_state.construct['url'],
                                auth=(st.session_state.construct['username'],
                                      st.session_state.construct['password'])
                            )
                            driver.verify_connectivity()
                            st.success("✅ Connection successful!")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
    else:
        iskg=False


    # use file
    use_file = st.checkbox(
        "📂 Use File",
        value=True if st.session_state.example_index >= 0
                      and examples[st.session_state.example_index].get("use_file", False) else False
    )

    text=""
    if use_file:
        #file_uploader
        uploaded_file = st.file_uploader("📖 Upload a File", type=["txt", "pdf", "html", "docx", "doc"])
        if uploaded_file is not None:
            try:
                file_path="data/input_files/"+uploaded_file.name
                raw_data = uploaded_file.getvalue()
                st.session_state.file_content = read_file_content(raw_data)
                st.success(f"Successfully loaded file: {file_path}")

                # preview file
                if st.session_state.file_content:
                    with st.expander("Preview uploaded file content"):
                        st.text_area("Uploaded File Preview",
                                     value=st.session_state.file_content[:5000],
                                     height=200,
                                     disabled=True)
            except Exception as e:
                st.error(f"Error reading uploaded file: {str(e)}")
        elif st.session_state.example_index >= 0 :
            file_path = examples[st.session_state.example_index].get("file_path")
            if file_path:
                try:
                    full_path = os.path.join(project_root, file_path)

                    # check if file exists
                    if os.path.exists(full_path):
                        # check file size
                        file_size = os.path.getsize(full_path)
                        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

                        if file_size > MAX_FILE_SIZE:
                            st.error(
                                f"File is too large ({file_size / 1024 / 1024:.2f}MB). Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB.")
                        else:
                            # read file
                            with open(full_path, "rb") as f:
                                raw_data = f.read()

                            content = read_file_content(raw_data)

                            if not content.strip():
                                st.warning("File appears to be empty")
                            elif len(content) < 100:
                                st.warning(f"File content is very short ({len(content)} characters)")

                            st.session_state.file_content = content
                            st.success(f"Successfully loaded file: {file_path}")

                            # preview file
                            with st.expander("Preview file content"):
                                st.text_area("File Content Preview",
                                             value=content[:5000],
                                             height=200,
                                             disabled=True)
                    else:
                        st.warning(f"File not found: {full_path}")
                except Exception as e:
                    st.error(f"Error loading file '{file_path}': {str(e)}")
            else:
                st.warning("No file path specified in this example")
    else:
        text = st.text_area(
            "📖 Text",
            height=150,
            value=(
                "" if st.session_state.example_index < 0 or examples[st.session_state.example_index].get("use_file",
                                                                                                         False)
                else examples[st.session_state.example_index].get("text", "")
            )
        )

    # constraint or instruction
    if task in ["NER", "RE", "EE", "Triple"]:
        constraint = st.text_area(
            "🕹️ Constraint",
            height=100,
            value="" if st.session_state.example_index < 0
            else examples[st.session_state.example_index].get("constraint", "")
        )
        instruction = ""
    else:
        instruction = st.text_area(
            "🕹️ Instruction",
            height=100,
            value="" if st.session_state.example_index < 0
            else examples[st.session_state.example_index].get("instruction", "")
        )
        constraint = ""

    # update case
    with st.expander("Advanced Options",expanded=True):
        update_case = st.checkbox(
            "💰 Update Case",
            value=False if st.session_state.example_index < 0
            else examples[st.session_state.example_index].get("update_case", False)
        )

        if update_case:
            truth = st.text_area(
                "🪙 Truth",
                height=100,
                value="" if st.session_state.example_index < 0
                else examples[st.session_state.example_index].get("truth", "")
            )
        else:
            truth = ""

    # submit and clear button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        if st.button("Submit", key="submit_btn", use_container_width=True):
            st.session_state.submit_pressed = True
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.example_index = -1
            st.session_state.submit_pressed = False
            st.session_state.file_content = ""
            st.session_state.ger_frontend_schema = None
            st.session_state.ger_frontend_res = None
            st.session_state.submit_completed = False
            st.rerun()

    #deal with submission
    if st.session_state.submit_pressed:
        try:
            # model configuration
            ModelClass = get_model_category(model)
            if base_url.strip() in ["", "Default"]:
                if api_key.strip() == "":
                    pipeline = Pipeline(ModelClass(model_name_or_path=model))
                else:
                    pipeline = Pipeline(ModelClass(model_name_or_path=model, api_key=api_key))
            else:
                if api_key.strip() == "":
                    pipeline = Pipeline(ModelClass(model_name_or_path=model, base_url=base_url))
                else:
                    pipeline = Pipeline(ModelClass(model_name_or_path=model, api_key=api_key, base_url=base_url))

            if use_file:
                text = ""
            else:
                file_path=None

            # agent configuration
            agent3 = {}
            if mode == "customized":
                if schema_agent != "Not Required":
                    agent3["schema_agent"] = schema_agent
                if extraction_agent != "Not Required":
                    agent3["extraction_agent"] = extraction_agent
                if reflection_agent != "Not Required":
                    agent3["reflection_agent"] = reflection_agent

            # pipeline
            _, _, ger_frontend_schema, ger_frontend_res = pipeline.get_extract_result(
                task=task,
                text=text,
                use_file=use_file,
                file_path=file_path if use_file else None,
                instruction=instruction,
                constraint=constraint,
                mode=mode,
                three_agents=agent3,
                isgui=True,
                update_case=update_case,
                truth=truth,
                output_schema="",
                show_trajectory=False,
                iskg=iskg,
                construct=st.session_state.construct
            )

            ger_frontend_schema = str(ger_frontend_schema)
            if isinstance(ger_frontend_res, dict):
                # save dictionary data for download
                download_data = json.dumps(ger_frontend_res, ensure_ascii=False, indent=4)
            else:
                download_data = str(ger_frontend_res)

            # save results to session_state
            st.session_state.ger_frontend_schema = ger_frontend_schema
            st.session_state.download_data = download_data
            st.session_state.ger_frontend_res = ger_frontend_res
            st.session_state.submit_completed = True  # task completed
            st.session_state.submit_pressed=False

        except Exception as e:
            st.error(f"⚠️ Error occurred:\n{str(e)}")

    # show results independently
    if st.session_state.get("submit_completed", False):
        # download button
        st.download_button(
            label="⬇️ Download JSON Result",
            data=st.session_state.download_data,
            file_name="extraction_result.json",
            mime="application/json"
        )

        # visualize knowledge
        if task == "Triple" and isinstance(st.session_state.ger_frontend_res, dict) and "triple_list" in st.session_state.ger_frontend_res:
            st.subheader("🧠 Knowledge Graph Visualization")
            visualize_knowledge_graph(st.session_state.ger_frontend_res)

        # show schema and final answer
        st.subheader("🤔 Generated Schema")
        st.code(st.session_state.ger_frontend_schema, language="python")

        st.subheader("😉 Final Answer")
        st.code(st.session_state.download_data, language="json")


if __name__ == "__main__":
    main()