
from tool import get_completion


'''
========================section1: model =========================

模型，langchain内置了很多对话模型，例如ChatOpenAI
from langchain.chat_models import ChatOpenAI
我们这里是痛殴deepseek创建的，直接使用get_completion()函数就ok，其内部执行的是：

result =  llm.invoke(prompt,temperature=temperature)
'''


'''
========================section2:使用提示模版======================
'''

from langchain.prompts import ChatPromptTemplate

# 首先，构造一个提示模版字符串：`template_string`
template_string = """把由三个反引号分隔的文本\
翻译成一种{style}风格。\
文本: ```{text}```
"""

# 创建了提示模版，有两个参数：`style`和`text`。
prompt_template = ChatPromptTemplate.from_template(template_string)



customer_style = """正式普通话 \
用一个平静、尊敬的语气
"""

customer_email = """
嗯呐，我现在可是火冒三丈，我那个搅拌机盖子竟然飞了出去，把我厨房的墙壁都溅上了果汁！
更糟糕的是，保修条款可不包括清理我厨房的费用。
伙计，赶紧给我过来！
"""

#使用提示模版，传入参数，注意上边是from_template，这里是format_messages
messages = prompt_template.format_messages(
                    style=customer_style,
                    text=customer_email)
# 打印客户消息类型
# print("客户消息类型:",type(customer_messages),"\n") #<class 'list'> 

# # 打印第一个客户消息类型
# print("第一个客户客户消息类型类型:", type(customer_messages[0]),"\n") #<class 'langchain_core.messages.human.HumanMessage'> 


'''
===========================section3: 格式化结果==============================
'''


customer_review = """\
这款吹叶机非常神奇。 它有四个设置：\
吹蜡烛、微风、风城、龙卷风。 \
两天后就到了，正好赶上我妻子的\
周年纪念礼物。 \
我想我的妻子会喜欢它到说不出话来。 \
到目前为止，我是唯一一个使用它的人，而且我一直\
每隔一天早上用它来清理草坪上的叶子。 \
它比其他吹叶机稍微贵一点，\
但我认为它的额外功能是值得的。
"""

review_template_2 = """\
对于以下文本，请从中提取以下信息：：

礼物：该商品是作为礼物送给别人的吗？
如果是，则回答 是的；如果否或未知，则回答 不是。

交货天数：产品到达需要多少天？ 如果没有找到该信息，则输出-1。

价钱：提取有关价值或价格的任何句子，并将它们输出为逗号分隔的 Python 列表。

文本: {text}

{format_instructions}
"""

prompt = ChatPromptTemplate.from_template(template=review_template_2)


from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser


gift_schema = ResponseSchema(name="礼物",
                             description="这件物品是作为礼物送给别人的吗？\
                            如果是，则回答 是的，\
                            如果否或未知，则回答 不是。")


delivery_days_schema = ResponseSchema(name="交货天数",
                                      description="产品需要多少天才能到达？\
                                      如果没有找到该信息，则输出-1。")

price_value_schema = ResponseSchema(name="价钱",
                                    description="提取有关价值或价格的任何句子，\
                                    并将它们输出为逗号分隔的 Python 列表")


response_schemas = [gift_schema, 
                    delivery_days_schema,
                    price_value_schema]

#parser接收scheme作为参数
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
#get一个标准的输出instuction
format_instructions = output_parser.get_format_instructions()


messages = prompt.format_messages(text=customer_review, format_instructions=format_instructions)

print("输出格式规定：",format_instructions)





response = get_completion(messages)


print("结果类型:", type(response))
print("结果:", response)

# ```json
# {
#         "礼物": "是的",
#         "交货天数": "2",
#         "价钱": "它比其他吹叶机稍微贵一点, 但我认为它的额外功能是值得的"
# }
# ```


# output parser 会自动将结果转换为json格式，所以可以直接打印
output_dict = output_parser.parse(response)

print("解析后的结果类型:", type(output_dict))
print("解析后的结果:", output_dict)




