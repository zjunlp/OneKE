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

# Proxy configuration function - supports user configuration
def set_proxy_config(enable_proxy=PROXY_CONFIG["default_enabled"], 
                    proxy_host=PROXY_CONFIG["default_host"], 
                    proxy_port=PROXY_CONFIG["default_port"]):
    """Set proxy configuration
    
    Args:
        enable_proxy (bool): Whether to enable the proxy
        proxy_host (str): Proxy server address
        proxy_port (str): Proxy port
    """
    if enable_proxy:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        for var in PROXY_CONFIG["environment_variables"]:
            if var == 'USE_PROXY':
                os.environ[var] = 'true'
            else:
                os.environ[var] = proxy_url
        print(f"🔧 Proxy enabled: {proxy_url}")
    else:
        # Clear proxy settings
        for key in PROXY_CONFIG["environment_variables"]:
            os.environ.pop(key, None)
        print("❌ Proxy disabled")

# Do not set proxy during initialization, wait for user configuration

# Add OneKE source path
oneke_path = ONEKE_CONFIG["source_path"]
if oneke_path.exists():
    sys.path.insert(0, str(oneke_path))
    
    try:
        from models import *
        from pipeline import Pipeline
        from utils import *
        ONEKE_AVAILABLE = True
        
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


examples = get_examples()

def get_model_category(model_name_or_path):
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



# Page configuration
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"]
)

# Initialize session state
for key, default_value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

def main():
    """Main application function"""
    
    # Page title and description - Based on OneKE project Streamlit frontend
    # Original OneKE project information (commented out):
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
    
    # Get current example data (must be defined before sidebar configuration)
    current_example = st.session_state.get("current_example") or {}
    
    # Random example button
    col_example1, col_example2, col_example3 = st.columns([1, 2, 1])
    with col_example2:
        if st.button("🎲 Quick Start with an Example 🎲", type="primary", use_container_width=True):
            example = start_with_example()
            st.session_state.current_example = example
            st.rerun()
    
    # Sidebar configuration
    sidebar_config = render_sidebar()
    
    # Extract variables from sidebar configuration
    model_name = sidebar_config["model_name"]
    api_key = sidebar_config["api_key"]
    base_url = sidebar_config["base_url"]
    task_type = sidebar_config["task_type"]
    mode = sidebar_config["mode"]
    agent_config = sidebar_config["agent_config"]
    neo4j_config = sidebar_config["neo4j_config"]
    
    # Set Neo4j related variables for compatibility with existing code
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
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📝 Input Configuration")
        
        # Input method selection
        default_use_file = current_example.get("use_file", False)
        use_file = st.checkbox(
            "📂 Use File",
            value=default_use_file,
            help="Choose between file upload or text input"
        )
        
        # File upload or text input
        input_text = ""
        uploaded_file = None
        example_file_loaded = False
        
        if use_file:
            # Check if there is an example file to load
            example_file_path = current_example.get("file_path")
            if example_file_path and os.path.exists(example_file_path):
                # Display example file information
                st.info(f"📁 Example file loaded: {os.path.basename(example_file_path)}")
                st.info("📄 File will be processed by OneKE backend")
                input_text = f"[File: {os.path.basename(example_file_path)}]"
                
                # Mark that the example file has been loaded
                example_file_loaded = True
            
            # If no example file is loaded, display file uploader
            if not example_file_loaded:
                uploaded_file = st.file_uploader(
                "📖 Upload a File",
                type=FILE_CONFIG["supported_extensions"],
                help="Upload a text file, PDF, Word document, HTML file, or JSON file"
            )
            
            if uploaded_file is not None:
                # All files will be processed by OneKE backend
                st.success(f"✅ Uploaded {uploaded_file.name} - will be processed by OneKE backend")
                input_text = f"[File uploaded: {uploaded_file.name}]"
            else:
                input_text = ""
        else:
            # Text input
            default_text = current_example.get("text", "")
            input_text = st.text_area(
                "📖 Text",
                value=default_text,
                height=UI_CONFIG["text_area_height"]["text_input"],
                placeholder=UI_CONFIG["placeholders"]["text_input"],
                help=UI_CONFIG["help_texts"]["text_input"]
            )
        
        if task_type == "Base":
            # Base task displays instruction and output_schema input
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
            
            # Base task constraint is forced to be empty
            constraint = ""
        else:
            # Other tasks only display constraint input, instruction uses preset values
            default_constraint = current_example.get("constraint", "")
            
            # Provide different constraint format prompts for different task types
            constraint_placeholder = TASK_CONFIG["constraint_placeholders"].get(task_type, 'Enter constraints')
            constraint_help = TASK_CONFIG["constraint_help_texts"].get(task_type, 'Define constraints for the task')
            
            constraint = st.text_area(
                "🕹️ Constraint",
                value=default_constraint,
                height=UI_CONFIG["text_area_height"]["constraint"],
                placeholder=constraint_placeholder,
                help=constraint_help
            )
            
            # Other tasks instruction and output_schema use preset values
            instruction = ""
            output_schema = ""
        
        # Update case options
        default_update_case = current_example.get("update_case", False)
        update_case = st.checkbox(
            "💰 Update Case",
            value=default_update_case,
            help=UI_CONFIG["help_texts"]["update_case"]
        )
        
        # Truth input (only displayed when updating case)
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
        
        # Execute extraction button
        if st.button("🚀 Submit", type="primary"):
            with st.spinner(f"Performing {task_type} extraction in {mode} mode..."):
                try:
                    # Recreate Pipeline according to the logic of the submit function in webui.py
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
                    
                    # Process parameters according to task type (following the original OneKE design)
                    if task_type == "Base":
                        # Base task: use instruction, constraint is forced to be empty
                        instruction = instruction
                        constraint = ""
                    else:
                        # Other tasks: use constraint, instruction is forced to be empty (using preset values from config)
                        instruction = ""
                        constraint = constraint
                    
                    schema_agent = agent_config.get("schema_agent", "Not Required") if mode == "customized" and agent_config else "Not Required"
                    extraction_Agent = agent_config.get("extraction_Agent", "Not Required") if mode == "customized" and agent_config else "Not Required"
                    reflection_agent = agent_config.get("reflection_agent", "Not Required") if mode == "customized" and agent_config else "Not Required"
                    
                    # Construct agent3 dictionary according to the logic of webui.py
                    agent3 = {}
                    if mode == "customized":
                        if schema_agent not in ["", "Not Required"]:
                            agent3["schema_agent"] = schema_agent
                        if extraction_Agent not in ["", "Not Required"]:
                            agent3["extraction_agent"] = extraction_Agent
                        if reflection_agent not in ["", "Not Required"]:
                            agent3["reflection_agent"] = reflection_agent
                    
                    # Process text and file_path parameters according to the logic in webui.py
                    if use_file:
                        text_param = ""
                        # Check if using example file
                        example_file_path = current_example.get("file_path")
                        if example_file_path and os.path.exists(example_file_path):
                            # Use example file path
                            file_path_param = example_file_path
                        elif uploaded_file is not None:
                            # For Streamlit, we need to handle the uploaded file
                            # Determine the file extension based on the file type
                            file_extension = os.path.splitext(uploaded_file.name)[1]
                            if not file_extension:
                                file_extension = '.txt'
                            
                            # Save the uploaded file to a temporary location
                            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=file_extension) as tmp_file:
                                # Reset file pointer to the beginning
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
                    
                    # Use the get_extract_result method of Pipeline to maintain consistency with webui.py
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
                    
                    # Process results according to the logic in webui.py
                    ger_frontend_schema = str(ger_frontend_schema)
                    ger_frontend_res = json.dumps(ger_frontend_res, ensure_ascii=False, indent=4) if isinstance(ger_frontend_res, dict) else str(ger_frontend_res)
                    
                    result = {
                        "success": True,
                        "schema": ger_frontend_schema,
                        "result": ger_frontend_res
                    }
                    st.session_state.extraction_results = result
                    st.success(f"Extraction completed successfully in {mode} mode!")
                    
                    # Clean up temporary files (but do not delete example files)
                    if use_file and file_path_param and os.path.exists(file_path_param):
                        # Only delete temporary files, do not delete example files
                        example_file_path = current_example.get("file_path")
                        if file_path_param != example_file_path:
                            try:
                                os.unlink(file_path_param)
                            except:
                                pass
                
                except Exception as e:
                    # Reference the error handling method in webui.py
                    error_message = f"⚠️ Error:\n {str(e)}"
                    result = {
                        "success": False,
                        "error": error_message
                    }
                    st.session_state.extraction_results = result
                    st.error(f"Extraction failed: {str(e)}")
                    
                    # Provide specific suggestions for connection errors
                    if "Connection error" in str(e) or "connection" in str(e).lower():
                        st.warning("💡 Connection Error Solutions:")
                        for i, solution in enumerate(ERROR_MESSAGES["connection_error_solutions"], 1):
                            st.write(f"{i}. {solution}")
                    
                    # Display detailed error information for debugging
                    with st.expander("Detailed Error Information"):
                        st.code(str(e))
        
        
        if st.button("🧹 Clear All"):
            st.session_state.extraction_results = None
            st.session_state.current_example = {}
            st.rerun()
    
    with col2:
        st.header("📊 Results")
        
        if st.session_state.extraction_results:
            result = st.session_state.extraction_results
            render_results(result, task_type)
        else:
            st.info("👆 Configure your model and input text to start extraction.")


if __name__ == "__main__":
    main()
