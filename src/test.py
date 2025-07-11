from neo4j import GraphDatabase


def test_aura_connection():
    # 使用您的实际信息
    URI = "neo4j+s://52bb44ac.databases.neo4j.io"
    USER = "neo4j"
    PASSWORD = "JjvWjR1XEBr-6hHYh1oAmlekinaNgl7xhWfRY0pGZP4"

    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        with driver.session() as session:
            # 创建测试节点
            session.run("CREATE (:TestNode {name: 'ConnectionTest'})")
            # 查询测试节点
            result = session.run("MATCH (n:TestNode) RETURN n.name AS name")
            record = result.single()
            print(f"✅ 连接成功! 节点值: {record['name']}")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False
    finally:
        if 'driver' in locals():
            driver.close()


# 执行测试
test_aura_connection()