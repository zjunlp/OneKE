from rapidfuzz import process

# 目标字符串
target_string = "Extract all information in the given text."

# 候选字符串列表
choices = ["Extract the persons in the news report.", "Extract the named entities in the text.", "Tell me the key information in the text."]

# 找出所有匹配的字符串及其得分
matches = process.extract(target_string, choices)

# 输出每个候选字符串的匹配得分
for match in matches:
    print(f"String: '{match[0]}'  Score: {match[1]}")
