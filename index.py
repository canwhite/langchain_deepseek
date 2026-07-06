from llm_ds import SingletonChatOpenAI
from prompts import messages
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

'''
在LangChain中，LLM调用过程高度抽象，
其由模型(Model）
提示词模版(Prompt Template)
输出解析器(Output parser) 
组成

'''

#Model
llm = SingletonChatOpenAI().llm
# output = llm.invoke(messages)
# print(output.content) # 其返


#创建task
class Task(BaseModel):
    task_name: str = Field(description="分析任务，得到任务名称")
    task_type: str = Field(description="分析任务，得到任务的类型")
    task_content: str = Field(description="分析任务，得到任务的内容")
    task_time: str = Field(description="分析任务，得到任务的时间")
    task_status: str = Field(description="分析任务，得到任务的状态,完成或未完成")


# 定义一个任务查询字符串
task_query = "如何在Cesium中集成Babylon？"

# 需要一个parser，根据task确定返回值
parser = JsonOutputParser(pydantic_object=Task)

# 定义一个 PromptTemplate 实例，用于生成提示字符串
# 该模板包含一个查询变量，用于在提示字符串中插入用户输入的查询
# 该模板还包含一个格式化说明变量，用于在提示字符串中插入解析器生成的格式化说明
prompt = PromptTemplate(
    template="根据用户输入的问题得到任务JSON.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    #上述parser就是为了确定返回json
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# taskchain
task_chain = prompt | llm | parser

# taskchain.invoke执行
task_data = task_chain.invoke({"query": task_query})
print(task_data) # 这里得到的是解析过的结果，而不是message对象




