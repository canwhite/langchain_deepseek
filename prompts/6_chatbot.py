from tool import get_completion,get_completion_from_messages
'''
了解如何利用会话形式，与具有个性化特性（或专门为特定任务或行为设计）的聊天机器人进行深度对话。
'''


'''
=====================Type1: 讲笑话=========================
'''

# assistant的角色是由系统指定的，system在这里的作用是定义assistant的行为和特性。
messages =  [  
{'role':'system', 'content':'你是一个像莎士比亚一样说话的助手。'},    
{'role':'user', 'content':'给我讲个笑话'},   
{'role':'assistant', 'content':'鸡为什么过马路'},   
{'role':'user', 'content':'我不知道'}  ]


'''
=====================Type2: 友好的聊天机器人=========================
'''
messages =  [  
{'role':'system', 'content':'你是个友好的聊天机器人。'},    
{'role':'user', 'content':'Hi, 我是Isa。'}  ]

response = get_completion_from_messages(messages, temperature=1)
print(response)

'''
=====================Type3: 构建上下文=========================
# messages =  [  
# {'role':'system', 'content':'你是个友好的聊天机器人。'},    
# {'role':'user', 'content':'好，你能提醒我，我的名字是什么吗？'}  ]
'''

#如上所述，模型不知道我们的名字，
#如果想让模型引用或 “记住” 对话的早期部分，
#则必须在模型的输入中提供早期的交流。我们将其称为上下文 (context) 。
messages =  [  
{'role':'system', 'content':'你是个友好的聊天机器人。'},
{'role':'user', 'content':'Hi, 我是Isa'},
{'role':'assistant', 'content': "Hi Isa! 很高兴认识你。今天有什么可以帮到你的吗?"},
{'role':'user', 'content':'是的，你可以提醒我, 我的名字是什么?'}  ]

