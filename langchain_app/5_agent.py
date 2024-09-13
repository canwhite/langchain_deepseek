from tool import get_completion, llm 
'''
代理的概念理解：
代理作为语言模型的外部模块，
可提供计算、逻辑、检索等功能的支持，使语言模型获得异常强大的推理和获取信息的超能力。

首先代理是语言模型的外部模块，
相当于一个外部程序，它与语言模型之间通过某种协议进行通信。
'''
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
# from langchain.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.agents.agent_toolkits import create_python_agent


'''
=======================section1: 使用LangChain内置工具llm-math和wikipedia============================
'''

# 工具
# ImportError: LLMMathChain requires the numexpr package. Please install it with `pip install numexpr`.
tools = load_tools(
    ["llm-math","wikipedia"], 
    llm=llm #第一步初始化的模型
)

# 初始化代理
# Use Use new agent constructor methods like create_react_agent, create_json_agent, create_structured_chat_agent, etc. instead.
agent= initialize_agent(
    tools, #第二步加载的工具
    llm, #第一步初始化的模型
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,  #代理类型
    handle_parsing_errors=True, #处理解析错误
    verbose = True #输出中间步骤
)
# agent("计算300的25%") 


question = "Tom M. Mitchell是一位美国计算机科学家，\
也是卡内基梅隆大学（CMU）的创始人大学教授。\
他写了哪本书呢？"

# agent(question) 

'''
=======================section2: 使用LangChain内置工具PythonREPLTool===========================
'''
agent = create_python_agent(
    llm,  #使用前面一节已经加载的大语言模型
    tool=PythonREPLTool(), #使用Python交互式环境工具 REPLTool
    verbose=True #输出中间步骤
)
customer_list = ["小明","小黄","小红","小蓝","小橘","小绿",]

# agent.run(f"将使用pinyin拼音库这些客户名字转换为拼音，并打印输出列表: {customer_list}。") 


'''
=======================section3: 定义自己的工具并在代理中使用===========================
'''

#自写tool
from langchain.agents import tool
from datetime import date

@tool
def time(text: str) -> str:
    """
    返回今天的日期，用于任何需要知道今天日期的问题。\
    输入应该总是一个空字符串，\
    这个函数将总是返回今天的日期，任何日期计算应该在这个函数之外进行。
    """
    return str(date.today())

# 初始化代理
agent= initialize_agent(
    tools=[time], #将刚刚创建的时间工具加入代理
    llm=llm, #初始化的模型
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,  #代理类型
    handle_parsing_errors=True, #处理解析错误
    verbose = True #输出中间步骤
)

# 使用代理询问今天的日期. 
# 注: 代理有时候可能会出错（该功能正在开发中）。如果出现错误，请尝试再次运行它。
agent("今天的日期是？") 