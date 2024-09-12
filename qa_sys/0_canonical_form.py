from tool import get_completion_from_messages


#系统消息是我们向语言模型传达讯息的语句，用户消息则是模拟用户的问题。例如:
# assistant ，可以给出一些预置条件

messages =  [  
{'role':'system', 
 'content':'你是一个助理， 并以 Seuss 苏斯博士的风格作出回答。'},    
{'role':'user', 
 'content':'就快乐的小鲸鱼为主题给我写一首短诗'},  
{"role":"assistant",'content':'我是一直快乐的小鲸鱼...'}

] 

response = get_completion_from_messages(messages, temperature=1)
print(response)
