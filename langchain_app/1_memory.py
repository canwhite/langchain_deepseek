# 初始化对话模型
from langchain.chains import ConversationChain # 对话链
from langchain.memory import ConversationBufferMemory
from tool import llm


''' 
===========================section1: 对话缓存存储=============================
'''


memory = ConversationBufferMemory()
# 可以直接添加内容到存储中
memory.save_context({"input": "你好，我叫皮皮鲁"}, {"output": "你好啊，我叫鲁西西"})
memory.load_memory_variables({})

# 当将verbose参数设置为False时，程序会以更简洁的方式运行，只输出关键的信息。
conversation = ConversationChain(llm=llm, memory = memory, verbose=True )


response = conversation.predict(input="你好, 我叫皮皮鲁")

response =  conversation.predict(input="1+1等于多少？")

response =  conversation.predict(input="我叫什么名字？")

print(response)

#查看储存缓存
print(memory.buffer) 




'''
==========================section2: 对话缓存窗口储存========================
可以决定存储多少个对话记忆，k=1表明只保留一个对话记忆
'''

'''
from langchain.memory import ConversationBufferWindowMemory
# k=1表明只保留一个对话记忆
memory = ConversationBufferWindowMemory(k=1)  
memory.save_context({"input": "你好，我叫皮皮鲁"}, {"output": "你好啊，我叫鲁西西"})
memory.save_context({"input": "很高兴和你成为朋友！"}, {"output": "是的，让我们一起去冒险吧！"})
memory.load_memory_variables({})

conversation = ConversationChain(llm=llm, memory = memory, verbose=True )

print("第一轮对话：")
print(conversation.predict(input="你好, 我叫皮皮鲁"))

print("第二轮对话：")
print(conversation.predict(input="1+1等于多少？"))

print("第三轮对话：")
print(conversation.predict(input="我叫什么名字？"))
'''


'''
========================section3: 对话字符缓存储存===========================
使用对话字符缓存记忆，内存将限制保存的token数量。
but deepseek 不支持
'''


'''
from langchain.memory import ConversationTokenBufferMemory
# get_num_tokens_from_messages() is not presently implemented for model cl100k_base.
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=30)
memory.save_context({"input": "朝辞白帝彩云间，"}, {"output": "千里江陵一日还。"})
memory.save_context({"input": "两岸猿声啼不住，"}, {"output": "轻舟已过万重山。"})
memory.load_memory_variables({})
'''

'''
=========================section4: 对话摘要缓存储存=============================
获取摘要
but deepseek不支持
'''

'''
from langchain.memory import ConversationSummaryBufferMemory
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)
memory.save_context({"input": "你好，我叫皮皮鲁"}, {"output": "你好啊，我叫鲁西西"})
memory.save_context({"input": "很高兴和你成为朋友！"}, {"output": "是的，让我们一起去冒险吧！"})
memory.save_context({"input": "今天的日程安排是什么？"}, {"output": f"{schedule}"})

print(memory.load_memory_variables({})['history'])
'''