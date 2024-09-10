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

'''
一个 token 一般对应 4 个字符或者四分之三个单词；对于中文输入，一个 token 一般对应一个或半个词。
不同模型有不同的 token 限制，
需要注意的是，这里的 token 限制是输入的 Prompt 和输出的 completion 的 token 数之和，
因此输入的 Prompt 越长，能输出的 completion 的上限就越低。 ChatGPT3.5-turbo 的 token 上限是 4096。
'''


#温度系数控制多样性，越大越高
#适用于单轮对话
def get_completion(prompt,temperature=0.7):
    result =  llm.invoke(prompt,temperature=temperature)
    return result.content

#可传入消息列表
def get_completion_from_messages(messages,temperature=0,max_tokens=500):
    result =  llm.invoke(
        input = messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    token_usage = result.response_metadata["token_usage"]

    token_dict = {
        'prompt_tokens':token_usage['prompt_tokens'],
        'completion_tokens':token_usage['completion_tokens'],
        'total_tokens':token_usage['total_tokens'],
    }
    print(token_dict)

    # print(result.response_metadata)
    return result.content


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False



