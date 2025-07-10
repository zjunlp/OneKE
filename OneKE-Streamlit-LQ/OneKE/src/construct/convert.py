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
    Generates Cypher query statements based on the provided JSON data.
    """
    cypher_statements = []
    parsed_data = json.loads(data)

    def create_statement(triple):
        head = triple.get("head")
        head_type = triple.get("head_type")
        relation = triple.get("relation")
        relation_type = triple.get("relation_type")
        tail = triple.get("tail")
        tail_type = triple.get("tail_type")

        # head_safe = sanitize_string(head) if head else None
        head_type_safe = sanitize_string(head_type) if head_type else None
        # relation_safe = sanitize_string(relation) if relation else None
        relation_type_safe = sanitize_string(relation_type) if relation_type else None
        # tail_safe = sanitize_string(tail) if tail else None
        tail_type_safe = sanitize_string(tail_type) if tail_type else None

        statement = ""
        if head:
            if head_type_safe:
                statement += f'MERGE (a:{head_type_safe} {{name: "{head}"}}) '
            else:
                statement += f'MERGE (a:UNTYPED {{name: "{head}"}}) '
        if tail:
            if tail_type_safe:
                statement += f'MERGE (b:{tail_type_safe} {{name: "{tail}"}}) '
            else:
                statement += f'MERGE (b:UNTYPED {{name: "{tail}"}}) '
        if relation:
            if head and tail: # Only create relation if head and tail exist.
                if relation_type_safe:
                    statement += f'MERGE (a)-[:{relation_type_safe} {{name: "{relation}"}}]->(b);'
                else:
                    statement += f'MERGE (a)-[:UNTYPED {{name: "{relation}"}}]->(b);'
            else:
                statement += ';' if statement != "" else ''
        else:
            if relation_type_safe: # if relation is not provided, create relation by `relation_type`.
                statement += f'MERGE (a)-[:{relation_type_safe} {{name: "{relation_type_safe}"}}]->(b);'
            else:
                statement += ';' if statement != "" else ''
        return statement

    if "triple_list" in parsed_data:
        for triple in parsed_data["triple_list"]:
            cypher_statements.append(create_statement(triple))
    else:
        cypher_statements.append(create_statement(parsed_data))

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

    # Write excuted cypher statements to a text file if you want.
    # with open("executed_statements.txt", 'a') as f:
    #     for statement in cypher_statements:
    #         f.write(statement + '\n')
    #     f.write('\n')

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
                "relation_type": "Actions",
                "tail": "Fantastic Beasts and Where to Find Them",
                "tail_type": "Book"
            },
            {
                "head": "Fantastic Beasts and Where to Find Them",
                "head_type": "Book",
                "relation": "extra section of",
                "relation_type": "Affiliation",
                "tail": "Harry Potter Series",
                "tail_type": "Book"
            },
            {
                "head": "J.K. Rowling",
                "head_type": "Person",
                "relation": "wrote",
                "relation_type": "Actions",
                "tail": "Harry Potter Series",
                "tail_type": "Book"
            },
            {
                "head": "Harry Potter Series",
                "head_type": "Book",
                "relation": "create",
                "relation_type": "Actions",
                "tail": "Dumbledore",
                "tail_type": "Person"
            },
            {
                "head": "Fantastic Beasts and Where to Find Them",
                "head_type": "Book",
                "relation": "mention",
                "relation_type": "Actions",
                "tail": "Dumbledore",
                "tail_type": "Person"
            },
            {
                "head": "Voldemort",
                "head_type": "Person",
                "relation": "afrid",
                "relation_type": "Emotion",
                "tail": "Dumbledore",
                "tail_type": "Person"
            },
            {
                "head": "Voldemort",
                "head_type": "Person",
                "relation": "robs",
                "relation_type": "Actions",
                "tail": "the Elder Wand",
                "tail_type": "Weapon"
            },
            {
                "head": "the Elder Wand",
                "head_type": "Weapon",
                "relation": "belong to",
                "relation_type": "Affiliation",
                "tail": "Dumbledore",
                "tail_type": "Person"
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

    # Generate Cypher query statements
    cypher_statements = generate_cypher_statements(test_data)

    # Print the generated Cypher query statements
    for statement in cypher_statements:
        print(statement)
    print("\n")

    # Execute the generated Cypher query statements
    execute_cypher_statements(
        uri="neo4j://localhost:7687", # your URI
        user="your_username", # your username
        password="your_password", # your password
        cypher_statements=cypher_statements,
    )
