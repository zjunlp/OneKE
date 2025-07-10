import pandas as pd
import gradio as gr
from json2html import *

# 示例嵌套数据（保持原始结构）
nested_data = {
    "title": "Who is Tulsi Gabbard? Meet Trump's pick for director of national intelligence",
    "summary": "Tulsi Gabbard, President-elect Donald Trump\u2019s choice for director of national intelligence, could face a challenging Senate confirmation battle due to her lack of intelligence experience and controversial views.",
    "publication_date": "December 4, 2024",
    "keywords": [
        "Tulsi Gabbard",
        "Donald Trump",
        "director of national intelligence",
        "confirmation battle",
        "intelligence agencies",
        "Russia",
        "Syria",
        "Bashar al-Assad",
    ],
    "events": [
        {
            "name": "Tulsi Gabbard's nomination for director of national intelligence",
            "people_involved": [
                {
                    "name": "Tulsi Gabbard",
                    "identity": "Former U.S. Representative",
                    "role": "Nominee for director of national intelligence",
                },
                {
                    "name": "Donald Trump",
                    "identity": "President-elect",
                    "role": "Nominator",
                },
                {
                    "name": "Tammy Duckworth",
                    "identity": "Democratic Senator",
                    "role": "Critic of Gabbard's nomination",
                },
                {
                    "name": "Olivia Troye",
                    "identity": "Former national security official",
                    "role": "Commentator on Gabbard's potential impact",
                },
            ],
            "process": "Gabbard's nomination is expected to lead to a Senate confirmation battle.",
        }
    ],
    "quotes": {
        "Tammy Duckworth": "The U.S. intelligence community has identified her as having troubling relationships with America\u2019s foes, and so my worry is that she couldn\u2019t pass a background check.",
        "Olivia Troye": "If Gabbard is confirmed, America\u2019s allies may not share as much information with the U.S.",
    },
    "viewpoints": [
        "Gabbard's lack of intelligence experience raises concerns about her ability to oversee 18 intelligence agencies.",
        "Her past comments and meetings with foreign adversaries have led to accusations of being a national security risk.",
    ],
}


def render_nested_table(data):
    """递归渲染嵌套结构为HTML表格"""
    if isinstance(data, dict):
        table_attrs = (
            'border="1" style="width:100%; border-collapse:collapse; margin:5px;"'
        )
        rows = []
        for k, v in data.items():
            rows.append(
                f"""
                <tr>
                    <td style="background:#f5f5f5; padding:8px;"><strong>{k}</strong></td>
                    <td style="padding:8px;">{render_nested_table(v)}</td>
                </tr>
            """
            )
        return f"<table {table_attrs}>{''.join(rows)}</table>"

    elif isinstance(data, list) and data and isinstance(data[0], dict):
        # 列表中的字典转换为多行表格
        headers = "".join(f"<th>{k}</th>" for k in data[0].keys())
        rows = []
        for item in data:
            rows.append(
                "<tr>"
                + "".join(f"<td>{render_nested_table(v)}</td>" for v in item.values())
                + "</tr>"
            )
        return f"<table border='1' style='width:100%'><tr>{headers}</tr>{''.join(rows)}</table>"

    elif isinstance(data, list):
        # 简单列表转换为逗号分隔
        return ", ".join(str(x) for x in data)

    else:
        return str(data)


# 添加CSS美化
css = """
.nested-table {
    margin: 0 !important;
    width: calc(100% - 10px) !important;
}
.nested-table th {
    background: #e0e0e0 !important;
}
"""


def construct_table(output):
    with open("src/output.txt", "w", encoding="utf-8") as f:
        f.write(output)


import json


def vis_table(json_output_gr):
    json_output_gr=json_output_gr.value
    def refresh_table():
        with open("src/output.txt", "r", encoding="utf-8") as f:
            output = f.read()
        output = json.loads(output)
        return gr.HTML(render_nested_table(output))
    with gr.Column(visible=True) as table:
        with gr.Row():
            refresh_btn = gr.Button("Refresh Table")
        with gr.Row():
            with open("src/output.txt", "r", encoding="utf-8") as f:
                output = f.read()
            if(json_output_gr==output):
                output = json.loads(output)
            else:
                output = json.loads(json_output_gr)    
            html = gr.HTML(render_nested_table(output))

    refresh_btn.click(fn=refresh_table, outputs=html)

    return table


# with gr.Blocks() as demo:
#     table = vis_table(output_str)

# demo.launch()
