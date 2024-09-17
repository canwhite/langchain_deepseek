from langchain.chains import ConversationChain # 对话链
from langchain.chains import LLMChain   
from langchain.prompts import ChatPromptTemplate  
from tool import llm
import warnings
import pandas as pd



warnings.filterwarnings('ignore')
'''
可以理解为一种任务的分解
'''

'''
=============================section1: 大语言模型链============================
'''

prompt = ChatPromptTemplate.from_template("描述制造{product}的一个公司的最佳名称是什么?")
# 生成一个语言模型链
chain = LLMChain(llm=llm, prompt=prompt) 
product = "大号床单套装"
# response = chain.run(product)
# print(response)


'''
=============================section2: 简单顺序链============================
针对一个输入一个输出
'''

from langchain.chains import SimpleSequentialChain

# 1）创建两个子链
# 提示模板 1 ：这个提示将接受产品并返回最佳名称来描述该公司
first_prompt = ChatPromptTemplate.from_template(   
    "描述制造{product}的一个公司的最好的名称是什么"
)
chain_one = LLMChain(llm=llm, prompt=first_prompt)

# 提示模板 2 ：接受公司名称，然后输出该公司的长为20个单词的描述
second_prompt = ChatPromptTemplate.from_template(   
    "写一个20字的描述对于下面这个\
    公司：{company_name}的"
)
chain_two = LLMChain(llm=llm, prompt=second_prompt)

#构建简单顺序链
overall_simple_chain = SimpleSequentialChain(chains=[chain_one, chain_two],
                                             verbose=True)

# product = "大号床单套装"
# overall_simple_chain.run(product)

'''
===================================section3: 顺序链====================================
当有多个输入或多个输出时，我们则需要使用顺序链（SequentialChain）来实现。
让我们选择一篇评论并通过整个链传递它，可以发现，原始review是法语，可以把英文review看做是一种翻译，接下来是根据英文review得到的总结，最后输出的是用法语原文进行的续写信息。

'''
from langchain.chains import SequentialChain


#子链1
# prompt模板 1: 翻译成英语（把下面的review翻译成英语）
first_prompt = ChatPromptTemplate.from_template(
    "把下面的评论review翻译成英文:"
    "\n\n{Review}"
)
# chain 1: 输入：Review    输出：英文的 Review
# 注意这里有一个对外key
chain_one = LLMChain(llm=llm, prompt=first_prompt, output_key="English_Review")

#子链2
# prompt模板 2: 用一句话总结下面的 review
second_prompt = ChatPromptTemplate.from_template(
    "请你用一句话来总结下面的评论review:"
    "\n\n{English_Review}"
)
# chain 2: 输入：英文的Review   输出：总结
chain_two = LLMChain(llm=llm, prompt=second_prompt, output_key="summary")


#子链3
# prompt模板 3: 下面review使用的什么语言
third_prompt = ChatPromptTemplate.from_template(
    "下面的评论review使用的什么语言:\n\n{Review}"
)
# chain 3: 输入：Review  输出：语言
chain_three = LLMChain(llm=llm, prompt=third_prompt, output_key="language")


#子链4
# prompt模板 4: 使用特定的语言对下面的总结写一个后续回复
fourth_prompt = ChatPromptTemplate.from_template(
    "使用特定的语言对下面的总结写一个后续回复:"
    "\n\n总结: {summary}\n\n语言: {language}"
)
# chain 4: 输入： 总结, 语言    输出： 后续回复
chain_four = LLMChain(llm=llm, prompt=fourth_prompt, output_key="followup_message")


#对四个子链进行组合
#输入：review    
#输出：英文review，总结，后续回复 
overall_chain = SequentialChain(
    chains=[chain_one, chain_two, chain_three, chain_four],
    input_variables=["Review"],
    output_variables=["English_Review", "summary","followup_message"],
    verbose=True
)

# df = pd.read_csv('../data/Data.csv')
# review = df.Review[5]
# overall_chain(review)

'''
=============================section4: 路由链=============================
一个相当常见但基本的操作是根据输入将其路由到一条链，具体取决于该输入到底是什么。
如果你有多个子链，每个子链都专门用于特定类型的输入，那么可以组成一个路由链，它首先决定将它传递给哪个子链，然后将它传递给那个链
主打一个多种情况都给你，命中哪个是哪个

'''
from langchain.chains.router import MultiPromptChain  #导入多提示链
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.prompts import PromptTemplate


'''
------------------1）不同类型问题的提示模版-----------------------
'''
physics_template = """你是一个非常聪明的物理专家。 \
你擅长用一种简洁并且易于理解的方式去回答问题。\
当你不知道问题的答案时，你承认\
你不知道.

这是一个问题:
{input}"""


#第二个提示适合回答数学问题
math_template = """你是一个非常优秀的数学家。 \
你擅长回答数学问题。 \
你之所以如此优秀， \
是因为你能够将棘手的问题分解为组成部分，\
回答组成部分，然后将它们组合在一起，回答更广泛的问题。

这是一个问题：
{input}"""


#第三个适合回答历史问题
history_template = """你是以为非常优秀的历史学家。 \
你对一系列历史时期的人物、事件和背景有着极好的学识和理解\
你有能力思考、反思、辩证、讨论和评估过去。\
你尊重历史证据，并有能力利用它来支持你的解释和判断。

这是一个问题:
{input}"""


#第四个适合回答计算机问题
computerscience_template = """ 你是一个成功的计算机科学专家。\
你有创造力、协作精神、\
前瞻性思维、自信、解决问题的能力、\
对理论和算法的理解以及出色的沟通技巧。\
你非常擅长回答编程问题。\
你之所以如此优秀，是因为你知道  \
如何通过以机器可以轻松解释的命令式步骤描述解决方案来解决问题，\
并且你知道如何选择在时间复杂性和空间复杂性之间取得良好平衡的解决方案。

这还是一个输入：
{input}"""

#对提示模版进行命名和描述
# 中文
prompt_infos = [
    {
        "名字": "物理学", 
        "描述": "擅长回答关于物理学的问题", 
        "提示模板": physics_template
    },
    {
        "名字": "数学", 
        "描述": "擅长回答数学问题", 
        "提示模板": math_template
    },
    {
        "名字": "历史", 
        "描述": "擅长回答历史问题", 
        "提示模板": history_template
    },
    {
        "名字": "计算机科学", 
        "描述": "擅长回答计算机科学问题", 
        "提示模板": computerscience_template
    }
]


'''
------------------2）构建目标链条，默认链条和依照目标链条创建路由链-----------------------
'''

'''# 2-1)构建目标链'''
destination_chains = {}
for p_info in prompt_infos:
    name = p_info["名字"]
    prompt_template = p_info["提示模板"]
    prompt = ChatPromptTemplate.from_template(template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    destination_chains[name] = chain  

destinations = [f"{p['名字']}: {p['描述']}" for p in prompt_infos]
destinations_str = "\n".join(destinations)
print(destinations_str)

'''# 2-2 根据目标链条，构建路由链'''
MULTI_PROMPT_ROUTER_TEMPLATE = """给语言模型一个原始文本输入，\
让其选择最适合输入的模型提示。\
系统将为您提供可用提示的名称以及最适合改提示的描述。\
如果你认为修改原始输入最终会导致语言模型做出更好的响应，\
你也可以修改原始输入。


<< 格式 >>
返回一个带有JSON对象的markdown代码片段，该JSON对象的格式如下：
```json
{{{{
    "destination": 字符串 \ 使用的提示名字或者使用 "DEFAULT"
    "next_inputs": 字符串 \ 原始输入的改进版本
}}}}

记住：“destination”必须是下面指定的候选提示名称之一，\
或者如果输入不太适合任何候选提示，\
则可以是 “DEFAULT” 。
记住：如果您认为不需要任何修改，\
则 “next_inputs” 可以只是原始输入。

<< 候选提示 >>
{destinations}

<< 输入 >>
{{input}}

<< 输出 (记得要包含 ```json)>>

样例:
<< 输入 >>
"什么是黑体辐射?"
<< 输出 >>
```json
{{{{
    "destination": 字符串 \ 使用的提示名字或者使用 "DEFAULT"
    "next_inputs": 字符串 \ 原始输入的改进版本
}}}}

"""
router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
    destinations=destinations_str
)

# 这里传入最终参数，注意用的是PromptTemplate，而不是ChatPromptTemplate
router_prompt = PromptTemplate(
    template=router_template, # 这里传入的是模版
    input_variables=["input"],# 这里传入的是输入变量
    output_parser=RouterOutputParser(), #这里传入的是输出解析器
)

router_chain = LLMRouterChain.from_llm(llm, router_prompt)


'''2-3) 创建默认链 '''
# 构建默认目标链
default_prompt = ChatPromptTemplate.from_template("{input}")
default_chain = LLMChain(llm=llm, prompt=default_prompt)



'''
------------------2）构建整体链-----------------------
'''
# 路由链路接收到信息，给到目标链路，然后目标链路返回结果，如果没有匹配到走default
chain = MultiPromptChain(router_chain=router_chain,    #l路由链路
                         destination_chains=destination_chains,   #目标链路
                         default_chain=default_chain,      #默认链路
                         verbose=True   
                        )
response =  chain.run("什么是黑体辐射？")
print(response)