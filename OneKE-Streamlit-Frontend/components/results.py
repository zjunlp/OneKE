import streamlit as st
import streamlit.components.v1 as components
import json
from pyvis.network import Network
from config.settings import NEO4J_CONFIG, KG_VISUALIZATION_CONFIG, UI_CONFIG, ERROR_MESSAGES

# 尝试导入Neo4j驱动
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None

def generate_cypher_from_result(result_str):
    """从抽取结果生成Cypher语句"""
    try:
        if isinstance(result_str, str):
            result_data = json.loads(result_str)
        else:
            result_data = result_str
        
        cypher_statements = []
        
        # 处理OneKE Triple任务的输出格式：{"triple_list": [...]}
        if isinstance(result_data, dict) and 'triple_list' in result_data:
            triple_list = result_data['triple_list']
            for item in triple_list:
                if isinstance(item, dict) and 'head' in item and 'relation' in item and 'tail' in item:
                    head = str(item['head']).replace("'", "\\'")
                    tail = str(item['tail']).replace("'", "\\'")
                    relation = str(item['relation']).replace("'", "\\'")
                    
                    # 使用类型信息（如果可用）
                    head_type = item.get('head_type', 'Entity')
                    tail_type = item.get('tail_type', 'Entity')
                    relation_type = item.get('relation_type', relation)
                    
                    cypher = f"MERGE (h:{head_type} {{name: '{head}'}})"
                    cypher += f"\nMERGE (t:{tail_type} {{name: '{tail}'}})"
                    cypher += f"\nMERGE (h)-[:{relation_type.replace(' ', '_').upper()}]->(t);"
                    cypher_statements.append(cypher)
        
        # 处理简单的三元组列表格式（向后兼容）
        elif isinstance(result_data, list):
            for item in result_data:
                if isinstance(item, dict) and 'head' in item and 'relation' in item and 'tail' in item:
                    head = str(item['head']).replace("'", "\\'")
                    tail = str(item['tail']).replace("'", "\\'")
                    relation = str(item['relation']).replace("'", "\\'")
                    
                    cypher = f"MERGE (h:Entity {{name: '{head}'}})"
                    cypher += f"\nMERGE (t:Entity {{name: '{tail}'}})"
                    cypher += f"\nMERGE (h)-[:{relation.replace(' ', '_').upper()}]->(t);"
                    cypher_statements.append(cypher)
        
        if not cypher_statements:
            return f"// No valid triples found in result. Expected format: {{\"triple_list\": [{{\"head\": \"...\", \"relation\": \"...\", \"tail\": \"...\"}}]}}"
        
        return "\n\n".join(cypher_statements)
    except Exception as e:
        return f"// Error generating Cypher: {str(e)}"

def test_neo4j_connection(neo4j_url, neo4j_username, neo4j_password):
    """测试Neo4j数据库连接"""
    if not NEO4J_AVAILABLE:
        return {"success": False, "error": ERROR_MESSAGES["neo4j_driver_not_available"]}
    
    try:
        # 验证输入参数
        if not neo4j_url or not neo4j_username or not neo4j_password:
            return {"success": False, "error": ERROR_MESSAGES["neo4j_missing_params"]}
        
        # 尝试连接
        driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_username, neo4j_password))
        
        # 测试连接
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' as message")
            message = result.single()["message"]
            
            # 获取数据库信息
            db_info = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
            db_details = db_info.single()
            db_name = db_details["name"] if db_details else "Neo4j"
            db_version = db_details["version"] if db_details else "Unknown"
        
        driver.close()
        return {
            "success": True, 
            "message": f"Connected to {db_name} {db_version}"
        }
    
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower():
            error_msg = ERROR_MESSAGES["neo4j_auth_failed"]
        elif "connection" in error_msg.lower():
            error_msg = ERROR_MESSAGES["neo4j_connection_failed"]
        return {"success": False, "error": error_msg}

def build_knowledge_graph(result_str, neo4j_url, neo4j_username, neo4j_password):
    """构建知识图谱到Neo4j数据库"""
    if not NEO4J_AVAILABLE:
        return {"success": False, "error": "Neo4j driver not available"}
    
    try:
        driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_username, neo4j_password))
        
        cypher_statements = generate_cypher_from_result(result_str)
        if not cypher_statements or cypher_statements.startswith("// Error"):
            return {"success": False, "error": "Failed to generate Cypher statements"}
        
        with driver.session() as session:
            # 执行Cypher语句
            for statement in cypher_statements.split("\n\n"):
                if statement.strip():
                    session.run(statement)
            
            # 获取统计信息
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            stats = f"Nodes: {node_count}\nRelationships: {rel_count}"
        
        driver.close()
        return {"success": True, "stats": stats}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_knowledge_graph_visualization(result_str):
    """从OneKE Triple抽取结果创建知识图谱可视化"""
    try:
        if isinstance(result_str, str):
            result_data = json.loads(result_str)
        else:
            result_data = result_str
        
        # 创建pyvis网络图
        net = Network(
            height=KG_VISUALIZATION_CONFIG["network_height"], 
            width=KG_VISUALIZATION_CONFIG["network_width"], 
            directed=True,
            notebook=False, 
            bgcolor=KG_VISUALIZATION_CONFIG["background_color"], 
            font_color=KG_VISUALIZATION_CONFIG["font_color"],
            cdn_resources='remote'
        )
        
        # 存储节点和边的信息
        nodes = set()
        edges = []
        
        # 处理OneKE Triple任务的输出格式：{"triple_list": [...]}
        if isinstance(result_data, dict) and 'triple_list' in result_data:
            triple_list = result_data['triple_list']
            for item in triple_list:
                if isinstance(item, dict) and 'head' in item and 'relation' in item and 'tail' in item:
                    head = str(item['head'])
                    tail = str(item['tail'])
                    relation = str(item['relation'])
                    
                    # 获取类型信息
                    head_type = item.get('head_type', 'Entity')
                    tail_type = item.get('tail_type', 'Entity')
                    
                    nodes.add((head, head_type))
                    nodes.add((tail, tail_type))
                    edges.append((head, tail, relation))
        
        # 处理简单的三元组列表格式（向后兼容）
        elif isinstance(result_data, list):
            for item in result_data:
                if isinstance(item, dict) and 'head' in item and 'relation' in item and 'tail' in item:
                    head = str(item['head'])
                    tail = str(item['tail'])
                    relation = str(item['relation'])
                    
                    nodes.add((head, 'Entity'))
                    nodes.add((tail, 'Entity'))
                    edges.append((head, tail, relation))
        
        if not nodes:
            return None, "No valid triples found for visualization"
        
        # 定义节点类型颜色
        type_colors = KG_VISUALIZATION_CONFIG["node_colors"]
        
        # 添加节点到网络图
        for node_name, node_type in nodes:
            color = type_colors.get(node_type, KG_VISUALIZATION_CONFIG["default_node_color"])
            net.add_node(
                node_name, 
                label=node_name, 
                title=f"Type: {node_type}",
                color=color,
                size=KG_VISUALIZATION_CONFIG["node_size"]
            )
        
        # 添加边到网络图
        for head, tail, relation in edges:
            net.add_edge(
                head, 
                tail, 
                label=relation,
                title=relation,
                color=KG_VISUALIZATION_CONFIG["edge_color"],
                width=KG_VISUALIZATION_CONFIG["edge_width"]
            )
        
        # 配置图形布局
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            },
            "nodes": {
                "font": {
                    "size": 12
                }
            },
            "edges": {
                "font": {
                    "size": 10,
                    "align": "middle"
                },
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 1
                    }
                }
            }
        }
        """)
        
        # 生成HTML
        html_content = net.generate_html()
        
        # 统计信息
        stats = f"Nodes: {len(nodes)}\nRelationships: {len(edges)}"
        
        return html_content, stats
        
    except Exception as e:
        return None, f"Error creating visualization: {str(e)}"

def render_results(result, task_type):
    """渲染结果展示组件"""
    if result and result.get("success", False):
        # 按照webui.py的格式显示结果
        st.markdown("""
        <div style="width: 100%; text-align: center; font-size: 16px; font-weight: bold; position: relative; margin: 20px 0;">
            <span style="position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 45%; border-top: 1px solid #ccc;"></span>
            <span style="position: relative; z-index: 1; background-color: white; padding: 0 10px;">Output:</span>
            <span style="position: absolute; right: 0; top: 50%; transform: translateY(-50%); width: 45%; border-top: 1px solid #ccc;"></span>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建选项卡来切换不同的视图
        if task_type == "Triple":
            # Triple任务显示两个选项卡：结果和知识图谱
            tab1, tab2 = st.tabs(["📄 Schema & Results", "🕸️ Knowledge Graph"])
            
            with tab1:
                _render_schema_and_results(result)
            
            with tab2:
                _render_knowledge_graph_tab(result)
        
        else:
            # 非Triple任务只显示Schema和Results
            _render_schema_and_results(result)
    
    else:
        # 显示错误信息，与webui.py的error_output_gr一致
        st.text_area(
            "😵‍💫 Ops, an Error Occurred",
            value=result.get("error", "Unknown error") if result else "No result available",
            height=UI_CONFIG["error_text_area_height"],
            disabled=True
        )

def _render_schema_and_results(result):
    """渲染Schema和Results部分"""
    col_schema, col_result = st.columns([1, 1.5])
    
    with col_schema:
        st.markdown("**🤔 Generated Schema**")
        schema_content = result.get("schema", "")
        st.code(schema_content, language="python", line_numbers=False)
        
        # 下载按钮
        if schema_content:
            st.download_button(
                label="📥 Download Schema",
                data=schema_content,
                file_name="generated_schema.json",
                mime="application/json",
                key="download_schema"
            )
    
    with col_result:
        st.markdown("**😉 Final Answer**")
        result_content = result.get("result", "")
        st.code(result_content, language="json", line_numbers=False)
        
        # 下载按钮
        if result_content:
            st.download_button(
                label="📥 Download Result",
                data=result_content,
                file_name="final_answer.json",
                mime="application/json",
                key="download_result"
            )

def _render_knowledge_graph_tab(result):
    """渲染知识图谱选项卡"""
    st.success("✅ Triple task detected - Knowledge Graph features are available!")
    
    # 生成知识图谱可视化
    html_content, viz_stats = create_knowledge_graph_visualization(result.get("result", ""))
    
    # 控制按钮区域
    button_col1, button_col2, button_col3, button_col4 = st.columns([1, 1, 1, 1])
    
    with button_col1:
        # 显示图谱统计信息
        if html_content:
            st.info(f"📊 {viz_stats}")
        else:
            st.error("❌ No graph data")
    
    with button_col2:
        if st.button("📄 Download Cypher", key="download_cypher", help="Download Cypher statements"):
            cypher_statements = generate_cypher_from_result(result.get("result", ""))
            if cypher_statements:
                st.download_button(
                    label="💾 Save Cypher File",
                    data=cypher_statements,
                    file_name="knowledge_graph.cypher",
                    mime="text/plain",
                    key="save_cypher"
                )
    
    with button_col3:
        if st.button("🔨 Build in Neo4j", key="build_neo4j", help="Build graph in Neo4j database"):
            if st.session_state.get("enable_kg_construction", False):
                with st.spinner("Building knowledge graph in Neo4j..."):
                    build_status = build_knowledge_graph(
                        result.get("result", ""),
                        st.session_state.get("neo4j_url", ""),
                        st.session_state.get("neo4j_username", ""),
                        st.session_state.get("neo4j_password", "")
                    )
                if build_status["success"]:
                    st.success("✅ Knowledge graph built successfully in Neo4j!")
                    st.info(f"📊 {build_status.get('stats', 'Graph built successfully')}")
                else:
                    st.error(f"❌ Failed to build knowledge graph: {build_status.get('error', 'Unknown error')}")
            else:
                st.warning("⚠️ Please enable 'Knowledge Graph Construction' in the configuration first.")
    
    with button_col4:
        # 添加全屏查看选项
        if 'fullscreen_graph' not in st.session_state:
            st.session_state.fullscreen_graph = False
        
        if st.button("🔍 Full Screen", key="fullscreen_btn", help="View graph in full screen"):
            st.session_state.fullscreen_graph = True
            st.rerun()
    
    # 检查是否进入全屏模式
    if st.session_state.fullscreen_graph:
        _render_fullscreen_graph(result, html_content, viz_stats)
    else:
        # 正常选项卡模式显示图谱
        if html_content:
            st.markdown("**Knowledge Graph Visualization:**")
            components.html(html_content, height=KG_VISUALIZATION_CONFIG["tab_view_height"], scrolling=True)
        else:
            st.error(f"❌ Failed to create visualization: {viz_stats}")

def _render_fullscreen_graph(result, html_content, viz_stats):
    """渲染全屏知识图谱视图"""
    st.markdown("### 🔍 Full Screen Knowledge Graph View")
    
    # 退出全屏按钮
    if st.button("⬅️ Back to Tab View", key="exit_fullscreen"):
        st.session_state.fullscreen_graph = False
        st.rerun()
    
    # 全屏图谱显示
    if html_content:
        # 使用更大的高度和全宽度显示
        components.html(html_content, height=KG_VISUALIZATION_CONFIG["fullscreen_height"], scrolling=True)
        
        # 全屏模式下的详细统计信息
        with st.expander("📊 Detailed Graph Statistics", expanded=False):
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.text_area(
                    "Graph Statistics",
                    value=viz_stats,
                    height=UI_CONFIG["stats_text_area_height"],
                    disabled=True
                )
            with col_stats2:
                # 显示图谱的详细信息
                try:
                    result_data = json.loads(result.get("result", "{}"))
                    if isinstance(result_data, dict) and 'triple_list' in result_data:
                        triple_count = len(result_data['triple_list'])
                        st.metric("Total Triples", triple_count)
                    else:
                        st.metric("Total Triples", "N/A")
                except:
                    st.metric("Total Triples", "N/A")
    else:
        st.error(f"❌ Failed to create visualization: {viz_stats}")