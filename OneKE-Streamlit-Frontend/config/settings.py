# -*- coding: utf-8 -*-
"""
OneKE-Streamlit-Frontend 配置文件
包含应用程序的所有配置项、默认值和常量
"""

import os
from pathlib import Path

# ==================== 应用程序基本配置 ====================
APP_CONFIG = {
    "page_title": "OneKE-Streamlit-Frontend",
    "page_icon": "🧠",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ==================== OneKE 路径配置 ====================
ONEKE_CONFIG = {
    "source_path": Path("../src"),
    "data_path": Path("../data"),
    "input_files_path": Path("../data/input_files")
}

# ==================== 模型配置 ====================
MODEL_CONFIG = {
    "default_model": "deepseek-chat",
    "default_api_key": "sk-xxxxxxxx",
    "default_base_url": "https://api.deepseek.com",
    "supported_models": {
        "gpt": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "o3-mini"],
        "deepseek": ["deepseek-chat", "deepseek-reasoner"],
        "llama": "llama",  # 正则匹配
        "qwen": "qwen",    # 正则匹配
        "minicpm": "minicpm",  # 正则匹配
        "chatglm": "chatglm"   # 正则匹配
    }
}

# ==================== 任务配置 ====================
TASK_CONFIG = {
    "supported_tasks": ["Base", "NER", "RE", "EE", "Triple"],
    "supported_modes": ["quick", "standard", "customized"],
    "default_task": "Base",
    "default_mode": "quick",
    "constraint_placeholders": {
        "NER": 'Enter entity types as a list, e.g., ["Person", "Location", "Organization"]',
        "RE": 'Enter relation types as a list, e.g., ["nationality", "country capital", "born in"]',
        "EE": 'Enter event schema as a dictionary, e.g., {"Conflict": ["Attacker", "Target", "Place"]}',
        "Triple": 'Enter constraints for Triple extraction'
    },
    "constraint_help_texts": {
        "NER": "Define entity types for Named Entity Recognition. Format: list of strings",
        "RE": "Define relation types for Relation Extraction. Format: list of strings",
        "EE": "Define event schema for Event Extraction. Format: dictionary with event types as keys and argument roles as values",
        "Triple": "Define constraints for Triple extraction"
    }
}

# ==================== Neo4j 配置 ====================
NEO4J_CONFIG = {
    "default_url": "neo4j://127.0.0.1:7687",
    "default_username": "neo4j",
    "default_password": "password",
    "connection_timeout": 10
}

# ==================== 代理配置 ====================
PROXY_CONFIG = {
    "default_host": "127.0.0.1",
    "default_port": "7890",
    "default_enabled": False,
    "environment_variables": [
        'http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'USE_PROXY'
    ]
}

# ==================== 文件上传配置 ====================
FILE_CONFIG = {
    "supported_extensions": ["txt", "pdf", "docx", "html", "json"],
    "max_file_size": 200 * 1024 * 1024,  # 200MB
    "temp_dir": None  # 使用系统默认临时目录
}

# ==================== UI 配置 ====================
UI_CONFIG = {
    "text_area_height": {
        "text_input": 200,
        "instruction": 100,
        "output_schema": 80,
        "constraint": 100,
        "truth": 80
    },
    "error_text_area_height": 200,
    "stats_text_area_height": 100,
    "placeholders": {
        "text_input": "Enter your Text please.",
        "instruction": "You can enter any type of information you want to extract here, for example: Please help me extract all the person names.",
        "output_schema": '{"type": "object", "properties": {"entities": {"type": "array"}}}',
        "truth": 'You can enter the truth you want LLM know, for example: {"relation_list": [{"head": "Guinea", "tail": "Conakry", "relation": "country capital"}]}'
    },
    "help_texts": {
        "use_file": "Choose between file upload or text input",
        "text_input": "Paste or type the text for information extraction",
        "instruction": "Provide specific instructions for the extraction task",
        "output_schema": "Define custom output schema for Base tasks. Leave empty to use default schema.",
        "update_case": "Enable case updates for improved extraction",
        "truth": "Provide ground truth information for case updates"
    }
}

# ==================== 错误消息配置 ====================
ERROR_MESSAGES = {
    "oneke_not_available": "OneKE source path not found. Using fallback implementations.",
    "neo4j_driver_not_available": "Neo4j driver not available. Please install: pip install neo4j",
    "neo4j_missing_params": "Please provide all connection parameters (URL, username, password)",
    "neo4j_auth_failed": "Authentication failed. Please check username and password.",
    "neo4j_connection_failed": "Connection failed. Please check URL and ensure Neo4j is running.",
    "connection_error_solutions": [
        "Check network connection",
        "Verify API key is correct",
        "Confirm Base URL settings",
        "Try disabling proxy settings",
        "Check firewall settings"
    ]
}

# ==================== 示例数据配置 ====================
EXAMPLES_CONFIG = {
    "chinese_news_file": "../data/input_files/ChineseNewsExample.json",
    "example_files": {
        "ai_wikipedia": "../data/input_files/Artificial_Intelligence_Wikipedia.txt",
        "harry_potter": "../data/input_files/Harry_Potter_Chapter1.pdf",
        "tulsi_gabbard": "../data/input_files/Tulsi_Gabbard_News.html"
    }
}

# ==================== 知识图谱可视化配置 ====================
KG_VISUALIZATION_CONFIG = {
    "network_height": "600px",
    "network_width": "100%",
    "background_color": "#ffffff",
    "font_color": "#000000",
    "node_size": 20,
    "edge_color": "#666666",
    "edge_width": 2,
    "default_node_color": "#cccccc",
    "tab_view_height": 500,
    "fullscreen_height": 700,
    "node_colors": {
        'Person': '#ff9999',
        'Place': '#99ff99', 
        'Event': '#9999ff',
        'Organization': '#ffff99',
        'Entity': '#cccccc',
        'Time': '#ff99ff',
        'Number': '#99ffff'
    }
}

# ==================== 会话状态默认值 ====================
SESSION_DEFAULTS = {
    "extraction_results": None,
    "current_example": {},
    "proxy_enabled": False,
    "proxy_host": "",
    "proxy_port": "",
    "neo4j_url": NEO4J_CONFIG["default_url"],
    "neo4j_username": NEO4J_CONFIG["default_username"],
    "neo4j_password": NEO4J_CONFIG["default_password"],
    "enable_kg_construction": False
}

# ==================== 环境变量配置 ====================
ENV_CONFIG = {
    "proxy_vars": PROXY_CONFIG["environment_variables"],
    "default_temp_dir": None
}

# ==================== 应用程序信息 ====================
APP_INFO = {
    "title": "OneKE-Streamlit-Frontend",
    "description": "基于OneKE项目的Streamlit知识抽取前端界面",
    "links": {
        "paper": "https://arxiv.org/abs/2412.20005v2",
        "code": "https://github.com/zjunlp/OneKE",
        "home": "http://oneke.openkg.cn/",
        "demo_video": "http://oneke.openkg.cn/demo.mp4"
    }
}

# ==================== 工具函数 ====================
def get_config_value(config_dict, key, default=None):
    """安全获取配置值"""
    return config_dict.get(key, default)

def update_config(config_dict, updates):
    """更新配置字典"""
    config_dict.update(updates)
    return config_dict

def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 检查OneKE路径
    if not ONEKE_CONFIG["source_path"].exists():
        errors.append(f"OneKE source path not found: {ONEKE_CONFIG['source_path']}")
    
    # 检查数据路径
    if not ONEKE_CONFIG["data_path"].exists():
        errors.append(f"OneKE data path not found: {ONEKE_CONFIG['data_path']}")
    
    return errors

# ==================== 配置初始化 ====================
def init_config():
    """初始化配置"""
    # 验证配置
    errors = validate_config()
    if errors:
        print("Configuration warnings:")
        for error in errors:
            print(f"  - {error}")
    
    return True

# 自动初始化
if __name__ != "__main__":
    init_config()