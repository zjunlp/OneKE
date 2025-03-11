import json
import re
from neo4j import GraphDatabase


def sanitize_string(input_str, max_length=255):
    """
    Process the input string to ensure it meets the database requirements.
    """
    # step1: Replace invalid characters
    input_str = re.sub(r'[^a-zA-Z0-9_]', '_', input_str)

    # step2: Add prefix if it starts with a digit
    if input_str[0].isdigit():
        input_str = 'num' + input_str

    # step3: Limit length
    if len(input_str) > max_length:
        input_str = input_str[:max_length]

    return input_str

def generate_cypher_statements(data):
    """
    enerates Cypher query statements based on the provided JSON data.
    """
    cypher_statements = []
    parsed_data = json.loads(data)

    # Handle a single triple (not in "triple_list")
    if "head" in parsed_data:
        triple = parsed_data
        head = triple["head"]
        head_type = triple["head_type"]
        relation = triple["relation"]
        relation_type = triple["relation_type"]
        tail = triple["tail"]
        tail_type = triple["tail_type"]

        # head_safe = sanitize_string(head)
        # relation_safe = sanitize_string(relation)
        # tail_safe = sanitize_string(tail)
        head_type_safe = sanitize_string(head_type)
        relation_type_safe = sanitize_string(relation_type)
        tail_type_safe = sanitize_string(tail_type)

        statement = (
            f'MERGE (a:{head_type_safe} {{name: "{head}"}}) '
            f'MERGE (b:{tail_type_safe} {{name: "{tail}"}}) '
            f'MERGE (a)-[:{relation_type_safe} {{name: "{relation}"}}]->(b);'
        )
        cypher_statements.append(statement)

    # Handle a list of triples in "triple_list"
    elif "triple_list" in parsed_data:
        for triple in parsed_data["triple_list"]:
            head = triple["head"]
            head_type = triple["head_type"]
            relation = triple["relation"]
            relation_type = triple["relation_type"]
            tail = triple["tail"]
            tail_type = triple["tail_type"]

            # head_safe = sanitize_string(head)
            # relation_safe = sanitize_string(relation)
            # tail_safe = sanitize_string(tail)
            head_type_safe = sanitize_string(head_type)
            relation_type_safe = sanitize_string(relation_type)
            tail_type_safe = sanitize_string(tail_type)

            statement = (
                f'MERGE (a:{head_type_safe} {{name: "{head}"}}) '
                f'MERGE (b:{tail_type_safe} {{name: "{tail}"}}) '
                f'MERGE (a)-[:{relation_type_safe} {{name: "{relation}"}}]->(b);'
            )
            cypher_statements.append(statement)

    return cypher_statements

def execute_cypher_statements(uri, user, password, cypher_statements):
    """
    Executes the generated Cypher query statements.
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        for statement in cypher_statements:
            session.run(statement)
            print(f"Executed: {statement}")

    driver.close()


# Here is a test of your database connection:
if __name__ == "__main__":
    # test_data 1: Contains a list of triples
    test_data = '''
    {
        "triple_list": [
            {
                "head": "J.K. Rowling",
                "head_type": "Person",
                "relation": "wrote",
                "relation_type": "authorship",
                "tail": "Harry Potter",
                "tail_type": "Book"
            },
            {
                "head": "Harry Potter",
                "head_type": "Book",
                "relation": "belongs to",
                "relation_type": "category",
                "tail": "Fantasy",
                "tail_type": "Genre"
            },
            {
                "head": "J.K. Rowling",
                "head_type": "Person",
                "relation": "belongs to",
                "relation_type": "category",
                "tail": "Fantasy",
                "tail_type": "Genre"
            }
        ]
    }
    '''

    # test_data 2: Contains a single triple
    # test_data = '''
    # {
    #     "head": "Christopher Nolan",
    #     "head_type": "Person",
    #     "relation": "directed",
    #     "relation_type": "Action",
    #     "tail": "Inception",
    #     "tail_type": "Movie"
    # }
    # '''

    cypher_statements = generate_cypher_statements(test_data)
    execute_cypher_statements(
        uri="neo4j://localhost:7687", # your URI
        user="your_username", # your username
        password="your_password", # your password
        cypher_statements=cypher_statements,
    )
