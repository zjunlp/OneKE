import os
import uuid
import base64
from pyvis.network import Network
from neo4j import GraphDatabase
import gradio as gr
import pandas as pd
from src.construct.convert import *
# === Neo4j 配置 ===
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "admin123"

# 初始化驱动
driver = GraphDatabase.driver(uri, auth=(username, password))


def visualize_neo4j(result):
    """将Neo4j查询结果可视化为交互式网络图"""
    if not result:
        return "<p>没有返回结果数据</p>"

    net = Network(
        height="750px",
        width="100%",
        bgcolor="#FFFFFF",
        font_color="black",
        notebook=False,
        filter_menu=True,
        cdn_resources="remote",
    )
    net.force_atlas_2based(gravity=-50)

    node_id_map = {}
    added_edges = set()

    for record in result:
        # 处理节点
        for key, value in record.items():
            if ("n" in key or "m" in key) and value is not None:
                neo4j_id = value.element_id
                if neo4j_id not in node_id_map:
                    labels = list(value.labels)
                    props = dict(value)
                    label = f"{':'.join(labels)}"
                    if props:
                        label += f"\n{props.get('name', props.get('title', ''))}"
                    net.add_node(
                        neo4j_id, label=label, title=str(props), group=labels[0]
                    )
                    node_id_map[neo4j_id] = neo4j_id

        # 处理关系
        for key, value in record.items():
            if "r" in key and value is not None:
                source = value.start_node.element_id
                target = value.end_node.element_id
                edge_key = (source, target, value.type)

                if edge_key not in added_edges:
                    net.add_edge(
                        source,
                        target,
                        title=f"{value.type}\n{str(dict(value))}",
                        label=value.type,
                        group=value.type,
                    )
                    added_edges.add(edge_key)

    # 生成HTML
    tmp_path = f"tmp_{uuid.uuid4().hex}.html"
    net.save_graph(tmp_path)

    with open(tmp_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    os.remove(tmp_path)
    encoded = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    return f'<iframe src="data:text/html;base64,{encoded}" width="100%" height="750px" frameborder="0"></iframe>'


def visualize_table(result):
    rows = []
    for record in result:
        row = {}
        for key, value in record.items():
            if hasattr(value, "labels"):  # Node
                row[f"{key}_labels"] = list(value.labels)
                row[f"{key}_props"] = dict(value)
            elif hasattr(value, "type"):  # Relationship
                row[f"{key}_type"] = value.type
                row[f"{key}_props"] = dict(value)
            else:
                row[key] = str(value)
        rows.append(row)
    df = pd.DataFrame(rows)
    return df.to_html(classes="dataframe", index=False)


def execute_query(query):
    """执行Neo4j查询并返回结果"""
    try:
        with driver.session() as session:
            return list(session.run(query))
    except Exception as e:
        print(f"查询执行错误: {e}")
        return []


def show_default_view(view_choice):
    """显示默认查询的视图"""
    default_query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50"
    return render_view(view_choice, default_query)


def render_view(view_choice, query):
    result = execute_query(query)
    if not result:
        return "<p>没有查询到数据或查询语法错误</p>"
    if view_choice == "可视化":
        return visualize_neo4j(result)
    else:
        return visualize_table(result)

def construct(output):
    cypher_statements=[]
    cypher_statements.append('MATCH (n) DETACH DELETE n;')
    cypher_statements += generate_cypher_statements(output)


    execute_cypher_statements(
        uri=uri, # your URI
        user=username, # your username
        password=password, # your password
        cypher_statements=cypher_statements,
    )
def vis_neo4j():
    with gr.Column(visible=False) as neo4j:  
        with gr.Row():
            query_input = gr.Textbox(
                label="Cypher 查询",
                placeholder="输入Cypher查询，如: MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN p,r,m",
                lines=3,
                value="MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50",
            )
        with gr.Row():
            submit_btn = gr.Button("执行查询", variant="primary")
            default_btn = gr.Button("显示全部")
        with gr.Row():
            view_radio = gr.Radio(
                choices=["可视化", "原始表格"], value="可视化", label="显示方式"
            )

        with gr.Row():
            output_display = gr.HTML()

    # 事件绑定
    submit_btn.click(
        fn=render_view, inputs=[view_radio, query_input], outputs=output_display
    )

    def show_default_view(view_choice):
        default_query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50"
        return render_view(view_choice, default_query)

    default_btn.click(
        fn=show_default_view, inputs=[view_radio], outputs=output_display
    )
    return neo4j
