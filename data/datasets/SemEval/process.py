import json

file_path = '/disk/disk_20T/luoyujie/Agent/OneKE-Agent-reconstruct/data/datasets/NYT11/train.jsonl'

result_list = []

with open(file_path, 'r') as file:
    for line in file:
        json_object = json.loads(line.strip())
        
        sentence = json_object['text']
        
        relation_list = []
        for rel in json_object['relation']:
            head = rel['head']
            relation = rel['relation']
            tail = rel['tail']
            
            relation_dict = {
                "head": head,
                "tail": tail,
                "relation": relation
            }
            relation_list.append(relation_dict)

        new_entry = {
            "sentence": sentence,
            "relation_list": relation_list  
        }
        result_list.append(new_entry)

output_file_path = '/disk/disk_20T/luoyujie/Agent/OneKE-Agent-reconstruct/data/datasets/NYT11/train.json'

with open(output_file_path, 'w') as output_file:
    json.dump(result_list, output_file, ensure_ascii=False, indent=4)

print(f"Result has been saved to {output_file_path}.")