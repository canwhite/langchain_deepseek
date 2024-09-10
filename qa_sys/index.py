from tool import get_completion_from_messages


messages =  [  
{'role':'system', 
 'content':'你是一个助理， 并以 Seuss 苏斯博士的风格作出回答。'},    
{'role':'user', 
 'content':'就快乐的小鲸鱼为主题给我写一首短诗'},  
] 
response = get_completion_from_messages(messages, temperature=1)
print(response)

