# -*- coding: utf-8 -*-
"""
OneKE-Streamlit-Frontend example data
Contains example data for various task types
"""

# Example data in OneKE webui.py
examples = [
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "合力治堵!济南交通部门在拥堵路段定点研究交通治理方案",
        "instruction": "请帮我抽取这个新闻事件",
        "constraint": "",
        "output_schema": '{"type": "object", "properties": {"events": {"type": "array", "items": {"type": "object", "properties": {"event_name": {"type": "string"}, "participants": {"type": "array"}, "location": {"type": "string"}}}}}}',
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "NER",
        "mode": "quick",
        "use_file": False,
        "text": "Finally, every other year , ELRA organizes a major conference LREC , the International Language Resources and Evaluation Conference .",
        "instruction": "",
        "constraint": '["algorithm", "conference", "else", "product", "task", "field", "metrics", "organization", "researcher", "program language", "country", "location", "person", "university"]',
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "RE",
        "mode": "quick",
        "use_file": False,
        "text": "The aid group Doctors Without Borders said that since Saturday , more than 275 wounded people had been admitted and treated at Donka Hospital in the capital of Guinea , Conakry .",
        "instruction": "",
        "constraint": '["nationality", "country capital", "place of death", "children", "location contains", "place of birth", "place lived", "administrative division of country", "country of administrative divisions", "company", "neighborhood of", "company founders"]',
        "file_path": None,
        "update_case": True,
        "truth": """{"relation_list": [{"head": "Guinea", "tail": "Conakry", "relation": "country capital"}]}""",
    },
    {
        "task": "EE",
        "mode": "standard",
        "use_file": False,
        "text": "The file suggested to the user contains no software related to video streaming and simply carries the malicious payload that later compromises victim \u2019s account and sends out the deceptive messages to all victim \u2019s contacts .",
        "instruction": "",
        "constraint": '{"phishing": ["damage amount", "attack pattern", "tool", "victim", "place", "attacker", "purpose", "trusted entity", "time"], "data breach": ["damage amount", "attack pattern", "number of data", "number of victim", "tool", "compromised data", "victim", "place", "attacker", "purpose", "time"], "ransom": ["damage amount", "attack pattern", "payment method", "tool", "victim", "place", "attacker", "price", "time"], "discover vulnerability": ["vulnerable system", "vulnerability", "vulnerable system owner", "vulnerable system version", "supported platform", "common vulnerabilities and exposures", "capabilities", "time", "discoverer"], "patch vulnerability": ["vulnerable system", "vulnerability", "issues addressed", "vulnerable system version", "releaser", "supported platform", "common vulnerabilities and exposures", "patch number", "time", "patch"]}',
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Triple",
        "mode": "quick",
        "use_file": True,
        "file_path": "../data/input_files/Artificial_Intelligence_Wikipedia.txt",
        "instruction": "",
        "constraint": '[["Person", "Place", "Event", "property"], ["Interpersonal", "Located", "Ownership", "Action"]]',
        "text": "",
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": True,
        "file_path": "../data/input_files/Harry_Potter_Chapter1.pdf",
        "instruction": "Extract main characters and the background setting from this chapter.",
        "constraint": "",
        "output_schema": '{"type": "object", "properties": {"characters": {"type": "array", "items": {"type": "string"}}, "setting": {"type": "object", "properties": {"location": {"type": "string"}, "time_period": {"type": "string"}}}}}',
        "text": "",
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": True,
        "file_path": "../data/input_files/Tulsi_Gabbard_News.html",
        "instruction": "Extract key information from the given text.",
        "constraint": "",
        "output_schema": '{"type": "object", "properties": {"key_information": {"type": "array", "items": {"type": "object", "properties": {"type": {"type": "string"}, "value": {"type": "string"}, "importance": {"type": "string"}}}}}}',
        "text": "",
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "John Smith, a 45-year-old male, presents with persistent headaches that have lasted for the past 10 days. The headaches are described as moderate and occur primarily in the frontal region, often accompanied by mild nausea. The patient reports no significant medical history except for seasonal allergies, for which he occasionally takes antihistamines. Physical examination reveals a heart rate of 78 beats per minute, blood pressure of 125/80 mmHg, and normal temperature. A neurological examination showed no focal deficits. A CT scan of the head was performed, which revealed no acute abnormalities, and a sinus X-ray suggested mild sinusitis. Based on the clinical presentation and imaging results, the diagnosis is sinusitis, and the patient is advised to take decongestants and rest for recovery.",
        "instruction": "Please extract the key medical information from this case description.",
        "constraint": "",
        "output_schema": '{"type": "object", "properties": {"patient_info": {"type": "object"}, "symptoms": {"type": "array"}, "diagnosis": {"type": "string"}, "treatment": {"type": "array"}}}',
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "张三，男，60岁，主诉背部酸痛已持续约两周，伴有轻微的头晕。患者有高血压病史，已服用降压药物多年，且控制良好；此外，患者曾在五年前接受过一次胆囊切除手术。体检时，心率为75次/分钟，血压为130/85 mmHg。背部触诊时无明显压痛，但活动时出现轻微不适。胸部X光显示无异常，腰部CT检查提示轻度腰椎退行性变。经医生诊断，患者被认为是由于长时间的不良姿势引起的腰椎退行性病变，建议进行物理治疗，并配合止痛药物。",
        "instruction": "请从这个病例描述中，提取出重要的医疗信息",
        "constraint": "",
        "output_schema": '{"type": "object", "properties": {"患者信息": {"type": "object"}, "症状": {"type": "array"}, "诊断": {"type": "string"}, "治疗方案": {"type": "array"}}}',
        "file_path": None,
        "update_case": False,
        "truth": "",
    },
    {
        "task": "Base",
        "mode": "quick",
        "use_file": False,
        "text": "中国政府近日宣布了一项新的环保政策，旨在减少工业污染，并改善空气质量。此次政策将在全国范围内实施，涉及多个行业，尤其是钢铁和煤炭行业。环保部门负责人表示，这项政策的实施标志着中国环保工作的新阶段，预计将在未来五年内显著改善空气质量。",
        "instruction": "请从这段新闻描述中提取出重要的事件信息，包括事件名称、时间、参与人员、事件目的、实施过程及预期结果。",
        "constraint": "",
        "output_schema": '{"type": "object", "properties": {"事件名称": {"type": "string"}, "时间": {"type": "string"}, "参与人员": {"type": "array"}, "事件目的": {"type": "string"}, "实施过程": {"type": "string"}, "预期结果": {"type": "string"}}}',
        "file_path": None,
        "update_case": False,
        "truth": "",
    }
]

def get_examples():
    """Get example data"""
    return examples

def get_example_by_task(task_type):
    """Get example by task type"""
    return [example for example in examples if example["task"] == task_type]

def get_example_by_index(index):
    """Get example by index"""
    if 0 <= index < len(examples):
        return examples[index]
    return None