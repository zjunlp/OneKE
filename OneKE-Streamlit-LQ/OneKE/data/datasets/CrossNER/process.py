import os
import json

def convert_entity_list(entity_list_dict):
    """将字典形式的 entity_list 转换为所需的列表形式"""
    return [{"name": name, "type": typ} for name, typ in entity_list_dict.items()]

def process_json(file_path):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as infile:
        try:
            data = json.load(infile)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from {file_path}: {e}")
            return

    # 处理每个对象的 entity_list
    for entry in data:
        if 'entity_list' in entry:
            entry['entity_list'] = convert_entity_list(entry['entity_list'])

    # 将处理后的数据写回到原始 JSON 文件
    with open(file_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

def process_all_json_files(base_path='.', filenames=['train.json', 'test.json']):
    for subdir, _, files in os.walk(base_path):
        for name in files:
            if name in filenames:
                file_path = os.path.join(subdir, name)
                print(f"Processing {file_path}")
                process_json(file_path)

# 运行业务逻辑
process_all_json_files()
