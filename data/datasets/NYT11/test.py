import json

def transform_jsonl_to_target_format(input_file, output_file):
    transformed_data = []
    
    with open(input_file, 'r') as file:
        for line in file:
            # 解析每一行的 JSON 数据
            entry = json.loads(line.strip())
            
            # 提取文本和关系列表
            sentence = entry['text']
            relations = entry['relation']
            
            # 重构为目标格式
            transformed_entry = {
                "sentence": sentence,
                "relation_list": [
                    {
                        "head": relation['head'],
                        "tail": relation['tail'],
                        "relation": relation['relation']
                    }
                    for relation in relations
                ]
            }

            # 添加到结果列表
            transformed_data.append(transformed_entry)
    
    # 将结果列表写入 JSON 文件
    with open(output_file, 'w') as file:
        json.dump(transformed_data, file, indent=4)

# 使用示例
input_file = '/disk/disk_20T/luoyujie/Agent/OneKE/OneKE-Agent/data/datasets/NYT11/train.jsonl'
output_file = '/disk/disk_20T/luoyujie/Agent/OneKE/OneKE-Agent/data/datasets/NYT11/train.json'
transform_jsonl_to_target_format(input_file, output_file)
