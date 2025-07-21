import streamlit as st
import os
import requests
from .proxy_config import render_proxy_configuration
from config.settings import (
    MODEL_CONFIG, TASK_CONFIG, NEO4J_CONFIG, ERROR_MESSAGES
)

# set_proxy_config 函数已移动到 components/proxy_config.py


def test_neo4j_connection(url, username, password):
    """测试Neo4j数据库连接"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(url, auth=(username, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                driver.close()
                return {"success": True, "message": "Connection successful"}
        driver.close()
        return {"success": False, "error": "Connection test failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_model_settings():
    """渲染模型设置部分"""
    st.subheader("Model Settings")
    
    # 获取当前示例数据
    current_example = st.session_state.get("current_example") or {}
    default_model = current_example.get("model", MODEL_CONFIG["default_model"])
    
    # 模型名称输入
    model_name = st.text_input(
        "🤖 Enter your Model",
        value=default_model,
        placeholder="Supports online-models like gpt-4o-mini, deepseek-chat, etc., while also allowing input of a path to use local models.",
        help="Enter model name or path"
    )
    
    # API Key
    api_key = st.text_input(
        "🔑 Enter your API-Key",
        value=MODEL_CONFIG["default_api_key"],
        type="password",
        placeholder="If using a local-model, this field should be left empty.",
        help="Enter your API key"
    )
    # 去除API key前后的空格
    api_key = api_key.strip()
    
    # Base URL
    base_url = st.text_input(
        "🔗 Enter your Base-URL",
        value="Default",
        placeholder="If using the default Base-URL or a local-model, this field should be left empty.",
        help="Enter custom base URL if needed"
    )
    # 去除Base URL前后的空格
    base_url = base_url.strip()
    
    # 模型配置完成提示
    st.info("💡 Model will be initialized automatically when you submit a task.")
    
    return model_name, api_key, base_url


def render_task_configuration():
    """渲染任务配置部分"""
    st.subheader("Task Configuration")
    
    # 获取当前示例数据
    current_example = st.session_state.get("current_example") or {}
    
    # 任务类型选择
    default_task = current_example.get("task", TASK_CONFIG["default_task"])
    task_type = st.selectbox(
        "🎯 Select your Task",
        TASK_CONFIG["supported_tasks"],
        index=TASK_CONFIG["supported_tasks"].index(default_task) if default_task in TASK_CONFIG["supported_tasks"] else 0,
        help="Choose the extraction task type"
    )
    
    # Neo4j配置 - 仅在Triple任务时显示
    neo4j_config = {}
    if task_type == "Triple":
        st.subheader("🗄️ Neo4j Database Configuration")
        neo4j_config["url"] = st.text_input(
            "Neo4j URL",
            value=NEO4J_CONFIG["default_url"],
            help="Neo4j database connection URL",
            key="neo4j_url"
        )
        neo4j_config["username"] = st.text_input(
            "Neo4j Username",
            value=NEO4J_CONFIG["default_username"],
            help="Neo4j database username",
            key="neo4j_username"
        )
        neo4j_config["password"] = st.text_input(
            "Neo4j Password",
            type="password",
            help="Neo4j database password",
            key="neo4j_password"
        )
        neo4j_config["enable_kg_construction"] = st.checkbox(
            "Enable Knowledge Graph Construction",
            value=False,
            help="Automatically build knowledge graph in Neo4j after extraction",
            key="enable_kg_construction"
        )
        
        # Neo4j连接测试
        if st.button("🔍 Test Neo4j Connection", key="test_neo4j"):
            test_result = test_neo4j_connection(
                neo4j_config["url"],
                neo4j_config["username"], 
                neo4j_config["password"]
            )
            if test_result["success"]:
                st.success(f"✅ Neo4j connection successful! {test_result['message']}")
            else:
                st.error(f"❌ Neo4j connection failed: {test_result['error']}")
                st.info("💡 Neo4j Connection Tips:")
                st.write("1. Make sure Neo4j database is running")
                st.write("2. Check URL format (e.g., bolt://localhost:7687)")
                st.write("3. Verify username and password")
                st.write("4. Check firewall settings")
                st.write("5. Ensure Neo4j driver is installed: pip install neo4j")
    
    # 模式选择
    default_mode = current_example.get("mode", TASK_CONFIG["default_mode"])
    mode = st.selectbox(
        "🧭 Select your Mode",
        TASK_CONFIG["supported_modes"],
        index=TASK_CONFIG["supported_modes"].index(default_mode) if default_mode in TASK_CONFIG["supported_modes"] else 0,
        help="Choose the extraction mode"
    )
    
    # 自定义模式的代理配置
    agent_config = {}
    if mode == "customized":
        st.subheader("Agent Configuration")
        
        agent_config["schema_agent"] = st.selectbox(
            "🤖 Select your Schema-Agent",
            ["Not Required", "get_default_schema", "get_retrieved_schema", "get_deduced_schema"],
            help="Choose schema generation agent"
        )            
        agent_config["extraction_Agent"] = st.selectbox(
            "🤖 Select your Extraction-Agent",
            ["Not Required", "extract_information_direct", "extract_information_with_case"],
            help="Choose extraction agent"
        )
        
        agent_config["reflection_agent"] = st.selectbox(
            "🤖 Select your Reflection-Agent",
            ["Not Required", "reflect_with_case"],
            help="Choose reflection agent"
        )
    
    return task_type, mode, agent_config, neo4j_config


# render_proxy_configuration 函数已移动到 components/proxy_config.py


def render_sidebar():
    """渲染完整的侧边栏"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # 模型设置
        model_name, api_key, base_url = render_model_settings()
        
        st.divider()
        
        # 任务配置
        task_type, mode, agent_config, neo4j_config = render_task_configuration()
        
        st.divider()
        
        # 代理配置
        render_proxy_configuration()
        
        return {
            "model_name": model_name,
            "api_key": api_key,
            "base_url": base_url,
            "task_type": task_type,
            "mode": mode,
            "agent_config": agent_config,
            "neo4j_config": neo4j_config
        }