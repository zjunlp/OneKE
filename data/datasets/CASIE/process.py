# import json

# def transform_record(record):
#     # 提取并转换记录中的信息
#     new_record = {
#         "sentence": record["text"],
#         "event_list": []
#     }
    
#     for event in record["event"]:
#         new_event = {
#             "event_type": event["event_type"],
#             "event_trigger": event["event_trigger"],
#             "arguments": {}
#         }
        
#         for argument in event["arguments"]:
#             role = argument["role"]
#             argument_text = argument["argument"]
#             new_event["arguments"][role] = argument_text
        
#         new_record["event_list"].append(new_event)
    
#     return new_record

# def transform_jsonl_to_list(input_file, output_file):
#     transformed_records = []
    
#     # 逐行读取 .jsonl 文件并转换其中的数据
#     with open(input_file, 'r', encoding='utf-8') as file:
#         for line in file:
#             record = json.loads(line.strip())
#             transformed_record = transform_record(record)
#             transformed_records.append(transformed_record)
    
#     # 保存结果到新的 JSON 文件
#     with open(output_file, 'w', encoding='utf-8') as file:
#         json.dump(transformed_records, file, indent=4)

# # 文件名
# input_file = '/disk/disk_20T/luoyujie/Agent/OneKE/OneKE-Agent/data/datasets/CASIE/train.jsonl'
# output_file = '/disk/disk_20T/luoyujie/Agent/OneKE/OneKE-Agent/data/datasets/CASIE/train.json'

# # 转换和保存
# transform_jsonl_to_list(input_file, output_file)
import json

data = [
    {
        "event_type": "phishing",
        "event_argument": [
            "damage amount",
            "attack pattern",
            "tool",
            "victim",
            "place",
            "attacker",
            "purpose",
            "trusted entity",
            "time"
        ]
    },
    {
        "event_type": "data breach",
        "event_argument": [
            "damage amount",
            "attack pattern",
            "number of data",
            "number of victim",
            "tool",
            "compromised data",
            "victim",
            "place",
            "attacker",
            "purpose",
            "time"
        ]
    },
    {
        "event_type": "ransom",
        "event_argument": [
            "damage amount",
            "attack pattern",
            "payment method",
            "tool",
            "victim",
            "place",
            "attacker",
            "price",
            "time"
        ]
    },
    {
        "event_type": "discover vulnerability",
        "event_argument": [
            "vulnerable system",
            "vulnerability",
            "vulnerable system owner",
            "vulnerable system version",
            "supported platform",
            "common vulnerabilities and exposures",
            "capabilities",
            "time",
            "discoverer"
        ]
    },
    {
        "event_type": "patch vulnerability",
        "event_argument": [
            "vulnerable system",
            "vulnerability",
            "issues addressed",
            "vulnerable system version",
            "releaser",
            "supported platform",
            "common vulnerabilities and exposures",
            "patch number",
            "time",
            "patch"
        ]
    }
]


one_line_json = json.dumps(data)
print(one_line_json)
