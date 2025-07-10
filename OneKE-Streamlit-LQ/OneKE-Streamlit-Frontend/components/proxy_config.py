import streamlit as st
import os
import requests
from config.settings import PROXY_CONFIG


def set_proxy_config(host, port):
    """设置代理配置"""
    proxy_url = f"http://{host}:{port}"
    for var in PROXY_CONFIG["environment_variables"]:
        if var == 'USE_PROXY':
            os.environ[var] = 'true'
        else:
            os.environ[var] = proxy_url
    print(f"代理已设置为: {proxy_url}")


def render_proxy_configuration():
    """渲染代理配置部分"""
    with st.expander("🌐 Proxy Configuration", expanded=False):
        st.markdown("**Configure proxy settings for better model downloading from Hugging Face**")
        
        # 启用代理复选框
        enable_proxy = st.checkbox(
            "Enable Proxy",
            value=st.session_state.get('proxy_enabled', PROXY_CONFIG["default_enabled"]),
            help="Enable proxy for network requests"
        )
        
        # 代理地址和端口输入
        col_proxy1, col_proxy2 = st.columns(2)
        with col_proxy1:
            proxy_host = st.text_input(
                "Proxy Host",
                value=st.session_state.get('proxy_host', PROXY_CONFIG["default_host"]),
                placeholder=f"e.g., {PROXY_CONFIG['default_host']}",
                help="Enter proxy server address"
            )
        
        with col_proxy2:
            proxy_port = st.text_input(
                "Proxy Port",
                value=st.session_state.get('proxy_port', PROXY_CONFIG["default_port"]),
                placeholder=f"e.g., {PROXY_CONFIG['default_port']}",
                help="Enter proxy server port"
            )
        
        # 应用代理设置按钮
        if st.button("Apply Proxy Settings", key="apply_proxy"):
            if enable_proxy and proxy_host and proxy_port:
                try:
                    set_proxy_config(proxy_host, proxy_port)
                    st.session_state['proxy_enabled'] = True
                    st.session_state['proxy_host'] = proxy_host
                    st.session_state['proxy_port'] = proxy_port
                    st.success(f"✅ Proxy enabled: {proxy_host}:{proxy_port}")
                except Exception as e:
                    st.error(f"❌ Failed to set proxy: {str(e)}")
            elif not enable_proxy:
                try:
                    # 禁用代理
                    if 'http_proxy' in os.environ:
                        del os.environ['http_proxy']
                    if 'https_proxy' in os.environ:
                        del os.environ['https_proxy']
                    st.session_state['proxy_enabled'] = False
                    st.success("✅ Proxy disabled")
                except Exception as e:
                    st.error(f"❌ Failed to disable proxy: {str(e)}")
            else:
                st.warning("⚠️ Please provide both proxy host and port")
        
        # 显示当前代理状态
        if st.session_state.get('proxy_enabled', False):
            current_host = st.session_state.get('proxy_host', '')
            current_port = st.session_state.get('proxy_port', '')
            st.info(f"🌐 Current proxy: {current_host}:{current_port}")
        else:
            st.info("🌐 Proxy: Disabled")
        
        # 测试代理连接按钮
        if st.button("Test Proxy Connection", key="test_proxy"):
            if st.session_state.get('proxy_enabled', False):
                with st.spinner("Testing proxy connection..."):
                    try:
                        # 测试连接到一个简单的网站
                        response = requests.get('https://httpbin.org/ip', timeout=10)
                        if response.status_code == 200:
                            st.success("✅ Proxy connection successful!")
                            st.json(response.json())
                        else:
                            st.error(f"❌ Proxy test failed with status code: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Proxy connection failed: {str(e)}")
            else:
                st.warning("⚠️ Please enable and configure proxy first")