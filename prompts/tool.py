import os
import sys
import json

# os.path.abspath(__file__) 获取当前文件的绝对路径。
# os.path.dirname() 获取指定路径的目录部分。
# 通过两次调用 os.path.dirname()，我们得到了当前文件的父目录的父目录。
# 最后，使用 sys.path.append() 将这个路径添加到系统路径中。

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_ds import SingletonChatOpenAI

llm = SingletonChatOpenAI().llm


def get_completion(prompt):
    result =  llm.invoke(prompt)
    return result.content

def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False



