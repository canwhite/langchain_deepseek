from tool import get_completion
import time
from IPython.display import display, Markdown, Latex, HTML, JSON
from redlines import Redlines
'''
大语言模型具有强大的文本转换能力，
可以实现多语言翻译、拼写纠正、语法调整、格式转换等不同类型的文本转换任务。 
'''

'''
======================Type1: 文本翻译====================
'''

# 1) 翻译为西班牙语

prompt = f"""
将以下中文翻译成西班牙语: \ 
```您好，我想订购一个搅拌机。```
"""

# 2）识别语种
prompt = f"""
请告诉我以下文本是什么语种: 
```Combien coûte le lampadaire?```
"""

# 3）多语种翻译

prompt = f"""
请将以下文本分别翻译成中文、英文、法语和西班牙语: 
```I want to order a basketball.```
"""

# 4）同时进行语气转换
prompt = f"""
请将以下文本翻译成中文，分别展示成正式与非正式两种语气: 
```Would you like to order a pillow?```
"""

# 5）通用翻译器
user_messages = [
  "La performance du système est plus lente que d'habitude.",  # System performance is slower than normal         
  "Mi monitor tiene píxeles que no se iluminan.",              # My monitor has pixels that are not lighting
  "Il mio mouse non funziona",                                 # My mouse is not working
  "Mój klawisz Ctrl jest zepsuty",                             # My keyboard has a broken control key
  "我的屏幕在闪烁"                                             # My screen is flashing
]

for issue in user_messages:
    # time.sleep(20)
    prompt = f"告诉我以下文本是什么语种，直接输出语种，如法语，无需输出标点符号: ```{issue}```"
    
    # lang = get_completion(prompt)
    # print(f"原始消息 ({lang}): {issue}\n")

    prompt = f"""
    将以下消息分别翻译成英文和中文，并写成
    中文翻译：xxx
    英文翻译：yyy
    的格式：
    ```{issue}```
    """
    # response = get_completion(prompt)
    # print(response, "\n=========================================")


'''
======================Type2: 语气和写作风格调整====================
'''


prompt = f"""
将以下文本翻译成商务信函的格式: 
```小老弟，我小羊，上回你说咱部门要采购的显示器是多少寸来着？```
"""



'''
======================Type3: 文本格式转换====================
更高效地处理结构化数据。
'''
data_json = { "resturant employees" :[ 
    {"name":"Shyam", "email":"shyamjaiswal@gmail.com"},
    {"name":"Bob", "email":"bob32@gmail.com"},
    {"name":"Jai", "email":"jai87@gmail.com"}
]}


prompt = f"""
将以下Python字典从JSON转换为HTML表格，保留表格标题和列名：{data_json}
只保留html信息，其他信息去除
"""

'''
======================Type4: 拼写和语法纠正====================
'''

text = f"""
Got this for my daughter for her birthday cuz she keeps taking \
mine from my room.  Yes, adults also like pandas too.  She takes \
it everywhere with her, and it's super soft and cute.  One of the \
ears is a bit lower than the other, and I don't think that was \
designed to be asymmetrical. It's a bit small for what I paid for it \
though. I think there might be other options that are bigger for \
the same price.  It arrived a day earlier than expected, so I got \
to play with it myself before I gave it to my daughter.
"""

prompt = f"校对并更正以下商品评论：```{text}```"


response = get_completion(prompt)
print(response)

'''
#关于type3显示HTML的代码

# 注意这个只能在Jupyter Notebook中运行
response = response.strip('```html').strip('```').strip()

display(HTML(response))

'''

'''
# 关于types4要显示比对错误
diff = Redlines(text,response)
display(Markdown(diff.output_markdown))

'''


