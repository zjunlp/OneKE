# -*- coding: utf-8 -*-
"""
OneKE-Streamlit-Frontend Configuration File
Contains all configuration items, default values, and constants for the application
"""

import os
from pathlib import Path

# ==================== Application Basic Configuration ====================
APP_CONFIG = {
    "page_title": "OneKE-Streamlit-Frontend",
    "page_icon": "💫",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ==================== OneKE Path Configuration ====================
ONEKE_CONFIG = {
    "source_path": Path("../src"),
    "data_path": Path("../data"),
    "input_files_path": Path("../data/input_files")
}

# ==================== Model Configuration ====================
MODEL_CONFIG = {
    "default_model": "deepseek-chat",
    "default_api_key": "sk-xxxxxxxx",
    "default_base_url": "https://api.deepseek.com",
    "supported_models": {
        "gpt": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "o3-mini"],
        "deepseek": ["deepseek-chat", "deepseek-reasoner"],
        "llama": "llama",  # Regular expression matching
        "qwen": "qwen",    # Regular expression matching
        "minicpm": "minicpm",  # Regular expression matching
        "chatglm": "chatglm"   # Regular expression matching
    }
}

# ==================== Task Configuration ====================
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

# ==================== Neo4j Configuration ====================
NEO4J_CONFIG = {
    "default_url": "neo4j://127.0.0.1:7687",
    "default_username": "neo4j",
    "default_password": "password",
    "connection_timeout": 10
}

# ==================== Proxy Configuration ====================
PROXY_CONFIG = {
    "default_host": "127.0.0.1",
    "default_port": "7890",
    "default_enabled": False,
    "environment_variables": [
        'http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'USE_PROXY'
    ]
}

# ==================== File Upload Configuration ====================
FILE_CONFIG = {
    "supported_extensions": ["txt", "pdf", "docx", "html", "json"],
    "max_file_size": 200 * 1024 * 1024,  # 200MB
    "temp_dir": None  # Use system default temporary directory
}

# ==================== UI Configuration ====================
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

# ==================== Error Messages Configuration ====================
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

# ==================== Example Data Configuration ====================
EXAMPLES_CONFIG = {
    "chinese_news_file": "../data/input_files/ChineseNewsExample.json",
    "example_files": {
        "ai_wikipedia": "../data/input_files/Artificial_Intelligence_Wikipedia.txt",
        "harry_potter": "../data/input_files/Harry_Potter_Chapter1.pdf",
        "tulsi_gabbard": "../data/input_files/Tulsi_Gabbard_News.html"
    }
}

# ==================== Knowledge Graph Visualization Configuration ====================
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

# ==================== Session State Defaults ====================
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

# ==================== Environment Variable Configuration ====================
ENV_CONFIG = {
    "proxy_vars": PROXY_CONFIG["environment_variables"],
    "default_temp_dir": None
}

# ==================== Application Information ====================
APP_INFO = {
    "title": "OneKE: A Flexible Schema-Guided Knowledge Extraction System",
    "description": "OneKE-Streamlit-Frontend",
    "links": {
        "paper": "https://arxiv.org/abs/2412.20005v2",
        "code": "https://github.com/zjunlp/OneKE",
        "home": "http://oneke.openkg.cn/",
        "demo_video": "http://oneke.openkg.cn/demo.mp4"
    }
}

# ==================== Utility Functions ====================
def get_config_value(config_dict, key, default=None):
    """Safely get configuration value"""
    return config_dict.get(key, default)

def update_config(config_dict, updates):
    """Update configuration dictionary"""
    config_dict.update(updates)
    return config_dict

def validate_config():
    """Validate the effectiveness of the configuration"""
    errors = []
    
    # Check OneKE path
    if not ONEKE_CONFIG["source_path"].exists():
        errors.append(f"OneKE source path not found: {ONEKE_CONFIG['source_path']}")
    
    # Check data path
    if not ONEKE_CONFIG["data_path"].exists():
        errors.append(f"OneKE data path not found: {ONEKE_CONFIG['data_path']}")
    
    return errors

# ==================== Configuration Initialization ====================
def init_config():
    """Initialize configuration"""
    # Validate configuration
    errors = validate_config()
    if errors:
        print("Configuration warnings:")
        for error in errors:
            print(f"  - {error}")
    
    return True

# Automatic initialization
if __name__ != "__main__":
    init_config()