import streamlit as st
import json
import os
import sys
import tempfile
import random
import re
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
from components.sidebar import render_sidebar
from components.results import render_results
from config.settings import (
    APP_CONFIG, MODEL_CONFIG, TASK_CONFIG, NEO4J_CONFIG, 
    PROXY_CONFIG, FILE_CONFIG, UI_CONFIG, ERROR_MESSAGES,
    ONEKE_CONFIG, APP_INFO, SESSION_DEFAULTS
)
from tools.examples import get_examples, get_example_by_index

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

# 代理设置函数 - 支持用户配置
def set_proxy_config(enable_proxy=PROXY_CONFIG["default_enabled"], 
                    proxy_host=PROXY_CONFIG["default_host"], 
                    proxy_port=PROXY_CONFIG["default_port"]):
    """设置代理配置
    
    Args:
        enable_proxy (bool): 是否启用代理
        proxy_host (str): 代理服务器地址
        proxy_port (str): 代理端口
    """
    if enable_proxy:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        for var in PROXY_CONFIG["environment_variables"]:
            if var == 'USE_PROXY':
                os.environ[var] = 'true'
            else:
                os.environ[var] = proxy_url
        print(f"🔧 代理已启用: {proxy_url}")
    else:
        # 清除代理设置
        for key in PROXY_CONFIG["environment_variables"]:
            os.environ.pop(key, None)
        print("❌ 代理已禁用")

# 初始化时不设置代理，等待用户配置
# print("⚙️ 代理配置将由用户在界面中设置")

# 添加OneKE源码路径
oneke_path = ONEKE_CONFIG["source_path"]
if oneke_path.exists():
    sys.path.insert(0, str(oneke_path))
    
    try:
        from models import *
        from pipeline import Pipeline
        from utils import *
        ONEKE_AVAILABLE = True
        
        # 尝试导入construct模块
        try:
            from construct.convert import generate_cypher_statements, execute_cypher_statements
            CONSTRUCT_AVAILABLE = True
        except ImportError:
            CONSTRUCT_AVAILABLE = False
    except ImportError as e:
        st.error(f"Failed to import OneKE modules: {e}")
        ONEKE_AVAILABLE = False
        CONSTRUCT_AVAILABLE = False
else:
    ONEKE_AVAILABLE = False
    CONSTRUCT_AVAILABLE = False
    st.warning(ERROR_MESSAGES["oneke_not_available"])

# OneKEProcessor不再需要，直接使用Pipeline


# 结果展示相关函数已移动到 components/results.py

# 导入示例数据

examples = get_examples()

def get_model_category(model_name_or_path):
    """获取模型类别，复制自webui.py"""
    if model_name_or_path in MODEL_CONFIG["supported_models"]["gpt"]:
        return ChatGPT
    elif model_name_or_path in MODEL_CONFIG["supported_models"]["deepseek"]:
        return DeepSeek
    elif re.search(r'(?i)' + MODEL_CONFIG["supported_models"]["llama"], model_name_or_path):
        return LLaMA
    elif re.search(r'(?i)' + MODEL_CONFIG["supported_models"]["qwen"], model_name_or_path):
        return Qwen
    elif re.search(r'(?i)' + MODEL_CONFIG["supported_models"]["minicpm"], model_name_or_path):
        return MiniCPM
    elif re.search(r'(?i)' + MODEL_CONFIG["supported_models"]["chatglm"], model_name_or_path):
        return ChatGLM
    else:
        return BaseEngine

def start_with_example():
    """随机选择一个示例，复制自webui.py"""
    example_index = random.randint(-3, len(examples) - 1)
    example_index = max(example_index, 0)
    example = get_example_by_index(example_index)
    
    if example_index == 0:
        from config.settings import EXAMPLES_CONFIG
        with open(EXAMPLES_CONFIG["chinese_news_file"], "r", encoding="utf-8") as file:
            lines = file.readlines()
            random_line = random.choice(lines).strip()
            try:
                json_data = json.loads(random_line)
                title = json_data.get("title", "No title found")
            except json.JSONDecodeError:
                title = "Error decoding JSON"
            example["text"] = title
    
    return example



# 页面配置
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"]
)

# 初始化session state
for key, default_value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

def main():
    """主应用函数"""
    
    # 页面标题和描述 - 基于OneKE项目的Streamlit前端
    # 原OneKE项目信息（已注释）:
    # OneKE: A Dockerized Schema-Guided LLM Agent-based Knowledge Extraction System
    # 🌐Home: http://oneke.openkg.cn/
    # 📹Video: http://oneke.openkg.cn/demo.mp4
    
    st.markdown(f"""
    <div style="text-align:center;">
        <h1>{APP_INFO["title"]}</h1>
        <p style="font-size: 18px; color: #666; margin-bottom: 10px;">
            {APP_INFO["description"]}
        </p>
        <p>
        📝<a href="{APP_INFO["links"]["paper"]}" target="_blank">OneKE Paper</a> |
        💻<a href="{APP_INFO["links"]["code"]}" target="_blank">OneKE Code</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取当前示例数据（必须在侧边栏配置之前定义）
    current_example = st.session_state.get("current_example") or {}
    
    # 随机示例按钮
    col_example1, col_example2, col_example3 = st.columns([1, 2, 1])
    with col_example2:
        if st.button("🎲 Quick Start with an Example 🎲", type="primary", use_container_width=True):
            example = start_with_example()
            st.session_state.current_example = example
            st.rerun()
    
    # 侧边栏配置
    sidebar_config = render_sidebar()
    
    # 从侧边栏配置中提取变量
    model_name = sidebar_config["model_name"]
    api_key = sidebar_config["api_key"]
    base_url = sidebar_config["base_url"]
    task_type = sidebar_config["task_type"]
    mode = sidebar_config["mode"]
    agent_config = sidebar_config["agent_config"]
    neo4j_config = sidebar_config["neo4j_config"]
    
    # 为了兼容现有代码，设置Neo4j相关变量
    if task_type == "Triple":
        neo4j_url = neo4j_config.get("url", "")
        neo4j_username = neo4j_config.get("username", "")
        neo4j_password = neo4j_config.get("password", "")
        enable_kg_construction = neo4j_config.get("enable_kg_construction", False)
    else:
        neo4j_url = ""
        neo4j_username = ""
        neo4j_password = ""
        enable_kg_construction = False
        

    
    # 主内容区域
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📝 Input Configuration")
        
        # 输入方式选择
        default_use_file = current_example.get("use_file", False)
        use_file = st.checkbox(
            "📂 Use File",
            value=default_use_file,
            help="Choose between file upload or text input"
        )
        
        # 文件上传或文本输入
        input_text = ""
        uploaded_file = None
        example_file_loaded = False
        
        if use_file:
            # 检查是否有示例文件需要加载
            example_file_path = current_example.get("file_path")
            if example_file_path and os.path.exists(example_file_path):
                # 显示示例文件信息
                st.info(f"📁 Example file loaded: {os.path.basename(example_file_path)}")
                st.info("📄 File will be processed by OneKE backend")
                input_text = f"[File: {os.path.basename(example_file_path)}]"
                
                # 标记示例文件已加载
                example_file_loaded = True
            
            # 如果没有加载示例文件，显示文件上传器
            if not example_file_loaded:
                uploaded_file = st.file_uploader(
                "📖 Upload a File",
                type=FILE_CONFIG["supported_extensions"],
                help="Upload a text file, PDF, Word document, HTML file, or JSON file"
            )
            
            if uploaded_file is not None:
                # 所有文件都交给OneKE后端处理
                st.success(f"✅ Uploaded {uploaded_file.name} - will be processed by OneKE backend")
                input_text = f"[File uploaded: {uploaded_file.name}]"
            else:
                input_text = ""
        else:
            # 文本输入
            default_text = current_example.get("text", "")
            input_text = st.text_area(
                "📖 Text",
                value=default_text,
                height=UI_CONFIG["text_area_height"]["text_input"],
                placeholder=UI_CONFIG["placeholders"]["text_input"],
                help=UI_CONFIG["help_texts"]["text_input"]
            )
        
        if task_type == "Base":
            # Base任务显示instruction和output_schema输入
            default_instruction = current_example.get("instruction", "")
            instruction = st.text_area(
                "🕹️ Instruction",
                value=default_instruction,
                height=UI_CONFIG["text_area_height"]["instruction"],
                placeholder=UI_CONFIG["placeholders"]["instruction"],
                help=UI_CONFIG["help_texts"]["instruction"]
            )
            
            default_output_schema = current_example.get("output_schema", "")
            output_schema = st.text_area(
                "📋 Output Schema (Optional)",
                value=default_output_schema,
                height=UI_CONFIG["text_area_height"]["output_schema"],
                placeholder=UI_CONFIG["placeholders"]["output_schema"],
                help=UI_CONFIG["help_texts"]["output_schema"]
            )
            
            # Base任务constraint强制为空
            constraint = ""
        else:
            # 其他任务只显示constraint输入，instruction使用预设值
            default_constraint = current_example.get("constraint", "")
            
            # 为不同任务类型提供不同的约束格式提示
            constraint_placeholder = TASK_CONFIG["constraint_placeholders"].get(task_type, 'Enter constraints')
            constraint_help = TASK_CONFIG["constraint_help_texts"].get(task_type, 'Define constraints for the task')
            
            constraint = st.text_area(
                "🕹️ Constraint",
                value=default_constraint,
                height=UI_CONFIG["text_area_height"]["constraint"],
                placeholder=constraint_placeholder,
                help=constraint_help
            )
            
            # 其他任务instruction和output_schema使用预设值
            instruction = ""
            output_schema = ""
        
        # 更新案例选项
        default_update_case = current_example.get("update_case", False)
        update_case = st.checkbox(
            "💰 Update Case",
            value=default_update_case,
            help=UI_CONFIG["help_texts"]["update_case"]
        )
        
        # 真值输入（仅在更新案例时显示）
        truth = ""
        if update_case:
            default_truth = current_example.get("truth", "")
            truth = st.text_area(
                "🪙 Truth",
                value=default_truth,
                height=UI_CONFIG["text_area_height"]["truth"],
                placeholder=UI_CONFIG["placeholders"]["truth"],
                help=UI_CONFIG["help_texts"]["truth"]
            )
        
        # 执行抽取按钮
        if st.button("🚀 Submit", type="primary"):
            with st.spinner(f"Performing {task_type} extraction in {mode} mode..."):
                try:
                    # 按照webui.py的submit函数逻辑重新创建Pipeline
                    ModelClass = get_model_category(model_name)
                    if base_url == "Default" or base_url == "":
                        if api_key == "":
                            pipeline = Pipeline(ModelClass(model_name_or_path=model_name))
                        else:
                            pipeline = Pipeline(ModelClass(model_name_or_path=model_name, api_key=api_key))
                    else:
                        if api_key == "":
                            pipeline = Pipeline(ModelClass(model_name_or_path=model_name, base_url=base_url))
                        else:
                            pipeline = Pipeline(ModelClass(model_name_or_path=model_name, api_key=api_key, base_url=base_url))
                    
                    # 根据任务类型处理参数（遵循原始OneKE设计）
                    if task_type == "Base":
                        # Base任务：使用instruction，constraint强制为空
                        instruction = instruction
                        constraint = ""
                    else:
                        # 其他任务：使用constraint，instruction强制为空（使用config中的预设值）
                        instruction = ""
                        constraint = constraint
                    
                    schema_agent = agent_config.get("schema_agent", "Not Required") if mode == "customized" and agent_config else "Not Required"
                    extraction_Agent = agent_config.get("extraction_Agent", "Not Required") if mode == "customized" and agent_config else "Not Required"
                    reflection_agent = agent_config.get("reflection_agent", "Not Required") if mode == "customized" and agent_config else "Not Required"
                    
                    # 按照webui.py的逻辑构建agent3字典
                    agent3 = {}
                    if mode == "customized":
                        if schema_agent not in ["", "Not Required"]:
                            agent3["schema_agent"] = schema_agent
                        if extraction_Agent not in ["", "Not Required"]:
                            agent3["extraction_agent"] = extraction_Agent
                        if reflection_agent not in ["", "Not Required"]:
                            agent3["reflection_agent"] = reflection_agent
                    
                    # 按照webui.py的逻辑处理text和file_path参数
                    if use_file:
                        text_param = ""
                        # 检查是否使用示例文件
                        example_file_path = current_example.get("file_path")
                        if example_file_path and os.path.exists(example_file_path):
                            # 使用示例文件路径
                            file_path_param = example_file_path
                        elif uploaded_file is not None:
                            # 对于Streamlit，我们需要处理上传的文件
                            # 根据文件类型确定后缀名
                            file_extension = os.path.splitext(uploaded_file.name)[1]
                            if not file_extension:
                                file_extension = '.txt'
                            
                            # 保存上传的文件到临时位置
                            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=file_extension) as tmp_file:
                                # 重置文件指针到开始位置
                                uploaded_file.seek(0)
                                tmp_file.write(uploaded_file.read())
                                file_path_param = tmp_file.name
                        else:
                            file_path_param = None
                    else:
                        text_param = input_text
                        file_path_param = None
                    
                    if not update_case:
                        truth = ""
                    
                    # 使用Pipeline的get_extract_result方法，与webui.py保持一致
                    _, _, ger_frontend_schema, ger_frontend_res = pipeline.get_extract_result(
                        task=task_type,
                        text=text_param,
                        use_file=use_file,
                        file_path=file_path_param,
                        instruction=instruction,
                        constraint=constraint,
                        mode=mode,
                        three_agents=agent3,
                        isgui=True,
                        update_case=update_case,
                        truth=truth,
                        output_schema=output_schema,
                        show_trajectory=False,
                    )
                    
                    # 按照webui.py的逻辑处理结果
                    ger_frontend_schema = str(ger_frontend_schema)
                    ger_frontend_res = json.dumps(ger_frontend_res, ensure_ascii=False, indent=4) if isinstance(ger_frontend_res, dict) else str(ger_frontend_res)
                    
                    result = {
                        "success": True,
                        "schema": ger_frontend_schema,
                        "result": ger_frontend_res
                    }
                    st.session_state.extraction_results = result
                    st.success(f"Extraction completed successfully in {mode} mode!")
                    
                    # 清理临时文件（但不删除示例文件）
                    if use_file and file_path_param and os.path.exists(file_path_param):
                        # 只删除临时文件，不删除示例文件
                        example_file_path = current_example.get("file_path")
                        if file_path_param != example_file_path:
                            try:
                                os.unlink(file_path_param)
                            except:
                                pass
                
                except Exception as e:
                    # 参考webui.py的错误处理方式
                    error_message = f"⚠️ Error:\n {str(e)}"
                    result = {
                        "success": False,
                        "error": error_message
                    }
                    st.session_state.extraction_results = result
                    st.error(f"Extraction failed: {str(e)}")
                    
                    # 提供连接错误的具体建议
                    if "Connection error" in str(e) or "connection" in str(e).lower():
                        st.warning("💡 Connection Error Solutions:")
                        for i, solution in enumerate(ERROR_MESSAGES["connection_error_solutions"], 1):
                            st.write(f"{i}. {solution}")
                    
                    # 显示详细错误信息用于调试
                    with st.expander("Detailed Error Information"):
                        st.code(str(e))
        
        
        # 清除按钮 - 与webui.py的clear_all行为一致
        if st.button("🧹 Clear All"):
            # 重置extraction_results和current_example
            st.session_state.extraction_results = None
            st.session_state.current_example = {}
            st.rerun()
    
    with col2:
        # 使用新的结果展示组件
        st.header("📊 Results")
        
        if st.session_state.extraction_results:
            result = st.session_state.extraction_results
            render_results(result, task_type)
        else:
            st.info("👆 Configure your model and input text to start extraction.")

# create_knowledge_graph_visualization 函数已移动到 components/results.py

if __name__ == "__main__":
    main()
