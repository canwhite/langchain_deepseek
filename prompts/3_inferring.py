from tool import get_completion, is_valid_json
import json
'''
引领你了解如何从产品评价和新闻文章中推导出情感和主题。
'''



'''
=====================Type1: 推导情感=========================
'''
# 1)情感倾向分析
lamp_review = """
我需要一盏漂亮的卧室灯，这款灯具有额外的储物功能，价格也不算太高。\
我很快就收到了它。在运输过程中，我们的灯绳断了，但是公司很乐意寄送了一个新的。\
几天后就收到了。这款灯很容易组装。我发现少了一个零件，于是联系了他们的客服，他们很快就给我寄来了缺失的零件！\
在我看来，Lumina 是一家非常关心顾客和产品的优秀公司！
"""
prompt = f"""
以下用三个反引号分隔的产品评论的情感是什么？

用一个单词回答：「正面」或「负面」。

评论文本: ```{lamp_review}```
"""

# 2）识别情感类型

# 中文
prompt = f"""
识别以下评论的作者表达的情感。包含不超过五个项目。将答案格式化为以逗号分隔的单词列表。

评论文本: 
```{lamp_review}```
"""

# 3) 识别愤怒
prompt = f"""
以下评论的作者是否表达了愤怒？评论用三个反引号分隔。给出是或否的答案。

评论文本: ```{lamp_review}```
"""







'''
=====================Type2: 信息提取=========================
'''


# 1） 信息提取
prompt = f"""
从评论文本中识别以下项目：
- 评论者购买的物品
- 制造该物品的公司

评论文本用三个反引号分隔。将你的响应格式化为以 “物品” 和 “品牌” 为键的 JSON 对象。
如果信息不存在，请使用 “未知” 作为值。
让你的回应尽可能简短。

评论文本: ```{lamp_review}```
"""

# 2）综合情感和信息

prompt = f"""
从评论文本中识别以下项目：
- 情绪（正面或负面）
- 审稿人是否表达了愤怒？（是或否）
- 评论者购买的物品
- 制造该物品的公司

评论用三个反引号分隔。将你的响应格式化为 JSON 对象，以 “情感倾向”、“是否生气”、“物品类型” 和 “品牌” 作为键。
如果信息不存在，请使用 “未知” 作为值。
让你的回应尽可能简短。
将 “是否生气” 值格式化为布尔值。

评论文本: ```{lamp_review}```
"""



''' 
=====================Type3: 推导主题=========================
'''
# 中文
story = """
在政府最近进行的一项调查中，要求公共部门的员工对他们所在部门的满意度进行评分。
调查结果显示，NASA 是最受欢迎的部门，满意度为 95％。

一位 NASA 员工 John Smith 对这一发现发表了评论，他表示：
“我对 NASA 排名第一并不感到惊讶。这是一个与了不起的人们和令人难以置信的机会共事的好地方。我为成为这样一个创新组织的一员感到自豪。”

NASA 的管理团队也对这一结果表示欢迎，主管 Tom Johnson 表示：
“我们很高兴听到我们的员工对 NASA 的工作感到满意。
我们拥有一支才华横溢、忠诚敬业的团队，他们为实现我们的目标不懈努力，看到他们的辛勤工作得到回报是太棒了。”

调查还显示，社会保障管理局的满意度最低，只有 45％的员工表示他们对工作满意。
政府承诺解决调查中员工提出的问题，并努力提高所有部门的工作满意度。
"""

# 1）推断讨论主题

prompt = f"""
确定以下给定文本中讨论的五个主题。

每个主题用1-2个词概括。

请输出一个可解析的Python列表，每个元素是一个字符串，展示了一个主题。

给定文本: ```{story}```
"""

# 2)给特定主题设置新闻提醒

# 中文
prompt = f"""
判断主题列表中的每一项是否是给定文本中的一个话题，

以列表的形式给出答案，每个元素是一个Json对象，键为对应主题，值为对应的 0 或 1。

主题列表：美国航空航天局、当地政府、工程、员工满意度、联邦政府

给定文本: ```{story}```
"""



response = get_completion(prompt)
print(response)

# 去除可能的 ```json 和 ``` 标记
response = response.strip('```json').strip('```').strip()
if is_valid_json(response):
    result_lst = json.loads(response)  # 使用 json.loads 解析 JSON 字符串
    topic_dict = {list(i.keys())[0] : list(i.values())[0] for i in result_lst}
    print(topic_dict)
    if topic_dict['美国航空航天局'] == 1:
        print("提醒: 关于美国航空航天局的新消息")
