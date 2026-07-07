# langchain_core 完整指南

## 1. 什么是 langchain_core

`langchain_core` 是 LangChain 生态系统的核心基础库，定义了 LangChain 所有关键组件的抽象接口。它具有以下特点：

- **模块化设计**：所有抽象接口相互独立，不依赖特定的模型提供商
- **稳定性强**：遵循稳定的版本控制策略，提前通知重大变更
- **轻量级依赖**：保持极简的依赖关系
- **生产就绪**：核心组件拥有 LLM 生态中最大的安装基数，被众多公司用于生产环境

### 安装方式

```bash
uv add langchain-core
```

### 核心模块概览

```
langchain_core/
├── messages/       # 消息抽象 (HumanMessage, AIMessage, SystemMessage)
├── prompts/       # 提示词模板 (ChatPromptTemplate, PromptTemplate)
├── output_parsers/ # 输出解析器 (JsonOutputParser, StrOutputParser)
├── language_models/ # 模型抽象 (BaseChatModel, BaseLLM)
├── runnables/      # 可运行接口和 LCEL
├── tools/         # 工具抽象 (BaseTool, tool)
├── callbacks/     # 回调处理器
├── documents/     # 文档抽象
├── retrievers/    # 检索器抽象
└── chat_history/ # 聊天历史
```

---

## 2. 消息系统 (Messages)

### 2.1 概述

消息是 LangChain 对话系统的基本单元，用于在用户、AI 和系统之间传递信息。

### 2.2 主要消息类型

| 类型 | 说明 |
|------|------|
| `HumanMessage` | 用户消息，代表用户输入 |
| `AIMessage` | AI 消息，代表模型回复 |
| `SystemMessage` | 系统消息，用于设置系统级指令 |
| `ToolMessage` | 工具消息，承载工具调用结果 |
| `FunctionMessage` | 函数消息（已弃用，推荐使用 ToolMessage） |
| `ChatMessage` | 通用聊天消息 |

### 2.3 代码示例

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 创建用户消息
human_msg = HumanMessage(content="你好，今天天气如何？")
print(human_msg.content)  # "你好，今天天气如何？"

# 创建 AI 消息
ai_msg = AIMessage(content="今天天气晴朗，气温25度。")

# 创建系统消息
system_msg = SystemMessage(content="你是一个有用的AI助手。")

# 消息也可以包含多模态内容
from langchain_core.messages import ImageContentBlock
human_with_image = HumanMessage(content=[
    {"type": "text", "text": "这张图片里有什么？"},
    {"type": "image", "source": {"type": "base64", "data": "..."}}
])
```

### 2.4 消息工具函数

```python
from langchain_core.messages import messages_to_dict, messages_from_dict, trim_messages, filter_messages

# 将消息列表转换为字典格式（用于序列化）
msgs = [HumanMessage(content="Hello"), AIMessage(content="Hi there!")]
msg_dicts = messages_to_dict(msgs)

# 从字典恢复消息列表
restored = messages_from_dict(msg_dicts)

# 修剪消息（控制对话长度）
trimmed = trim_messages(
    msgs,
    max_tokens=100,
    strategy="last"
)

# 过滤特定类型的消息
filtered = filter_messages(msgs, include_types=["human"])
```

### 2.5 使用场景

- **对话系统**：构建多轮对话应用
- **聊天机器人**：处理用户与 AI 的交互
- **工具调用**：传递工具执行结果
- **系统提示**：设置 AI 行为规则

---

## 3. 提示词模板 (Prompts)

### 3.1 概述

提示词模板用于动态构建发送给模型的输入，支持变量插值和消息组合。

### 3.2 主要模板类型

| 类型 | 说明 |
|------|------|
| `PromptTemplate` | 字符串模板，用于简单文本提示 |
| `ChatPromptTemplate` | 聊天消息模板组合 |
| `MessagesPlaceholder` | 动态插入消息列表 |
| `FewShotPromptTemplate` | 小样本学习模板 |
| `FewShotChatMessagePromptTemplate` | 聊天格式的小样本模板 |

### 3.3 PromptTemplate - 字符串模板

```python
from langchain_core.prompts import PromptTemplate

# 基本用法，这里可以直接使用字符串
prompt = PromptTemplate.from_template("请告诉我关于{topic}的信息")
result = prompt.invoke({"topic": "Python编程"})
print(result)  # PromptValue(text='请告诉我关于Python编程的信息')

# 手动创建
prompt = PromptTemplate(
    input_variables=["name", "age"],
    template="我叫{name}，今年{age}岁。"
)
result = prompt.invoke({"name": "张三", "age": 25})
```

### 3.4 ChatPromptTemplate - 聊天模板

```python
from langchain_core.prompts import ChatPromptTemplate

# 从字符串创建
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{profession}。"),
    ("human", "你好，请介绍一下你自己。"),
    ("ai", "您好！我是一名{profession}，很高兴为您服务。"),
    ("human", "请告诉我关于{topic}的信息。")
])

# 填充变量，invoke的时候可以直接直接定义好参数，
# prompt就可以直接invoke
result = prompt.invoke({
    "profession": "医生",
    "topic": "高血压"
})

# 查看生成的消息
for message in result.messages:
    print(f"{message.type}: {message.content}")
```

### 3.5 MessagesPlaceholder - 动态消息插入

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 动态插入聊天历史
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# 注入聊天历史
from langchain_core.messages import HumanMessage, AIMessage
result = prompt.invoke({
    "chat_history": [
        HumanMessage(content="我叫张三"),
        AIMessage(content="你好张三，有什么可以帮助你的吗？")
    ],
    "question": "我叫什么名字？"
})
```

### 3.6 Few-Shot 小样本学习

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

# 定义示例
examples = [
    {"word": "开心", "antonym": "难过"},
    {"word": "高", "antonym": "矮"}
]

# 创建示例模板
example_prompt = PromptTemplate(
    input_variables=["word", "antonym"],
    template="单词: {word}\n反义词: {antonym}"
)

# 创建小样本模板
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请给出以下单词的反义词：",
    suffix="单词: {input}\n反义词:",
    input_variables=["input"]
)

result = few_shot_prompt.invoke({"input": "漂亮"})
```

### 3.7 使用场景

- **动态提示构建**：根据用户输入动态生成提示
- **对话管理**：组合系统消息和聊天历史
- **小样本学习**：通过示例引导模型输出
- **多模态内容**：支持文本、图像等混合内容

---

## 4. 输出解析器 (Output Parsers)

### 4.1 概述

输出解析器将模型的原始输出转换为结构化数据。

### 4.2 主要解析器类型

| 类型 | 说明 |
|------|------|
| `StrOutputParser` | 直接返回字符串 |
| `JsonOutputParser` | 解析 JSON 输出 |
| `PydanticOutputParser` | 使用 Pydantic 模型验证 |
| `CommaSeparatedListOutputParser` | 解析逗号分隔的列表 |
| `XMLOutputParser` | 解析 XML 格式输出 |

### 4.3 StrOutputParser

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
#parser也可以invoke
result = parser.invoke("Hello, World!")
print(result)  # "Hello, World!"
```

### 4.4 JsonOutputParser

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# 定义 JSON 架构
parser = JsonOutputParser()

# 创建提示词模板
prompt = PromptTemplate.from_template(
    "请生成一个关于{topic}的JSON对象，包含name和age字段。"
)

# 组合 chain
chain = prompt | parser

# 调用
result = chain.invoke({"topic": "一个人"})
print(result)  # {'name': '...', 'age': ...}
print(type(result))  # <class 'dict'>
```

### 4.5 PydanticOutputParser - Pydantic 验证

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

# 定义 Pydantic 模型
class Person(BaseModel):
    name: str = Field(description="人的姓名")
    age: int = Field(description="人的年龄")
    city: str = Field(description="所在城市", default="未知")

# 创建解析器
parser = PydanticOutputParser(pydantic_object=Person)

# 创建提示词
prompt = PromptTemplate.from_template(
    "请生成一个人的信息。\n{format_instructions}",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 使用 chain
chain = prompt | parser

result = chain.invoke({})
print(result)  # Person(name='...', age=..., city='...')
print(result.name)
print(result.age)
```

### 4.6 列表输出解析器

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser, MarkdownListOutputParser

# 逗号分隔列表
list_parser = CommaSeparatedListOutputParser()
result = list_parser.invoke("apple, banana, orange")
print(result)  # ['apple', 'banana', 'orange']

# Markdown 列表
md_parser = MarkdownListOutputParser()
result = md_parser.invoke("- item1\n- item2\n- item3")
print(result)  # ['item1', 'item2', 'item3']
```

### 4.7 使用场景

- **结构化数据提取**：从模型输出中提取结构化信息
- **数据验证**：使用 Pydantic 自动验证输出格式
- **列表提取**：提取模型输出的列表数据
- **格式转换**：将自然语言输出转换为程序可用格式

---

## 5. 模型抽象 (Models)

### 5.1 概述

LangChain 定义了两种主要的模型接口：
- **Chat Models**：使用消息序列作为输入和输出
- **LLMs**：传统的字符串输入输出模型

### 5.2 BaseChatModel

```python
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.messages import BaseMessage, HumanMessage
from abc import ABC, abstractmethod

class MyChatModel(BaseChatModel):
    """自定义聊天模型示例"""

    @property
    def _llm_type(self) -> str:
        return "my-chat-model"

    def _generate(
        self,
        messages: list[BaseMessage],
        **kwargs
    ) -> ChatResult:
        # 实现生成逻辑
        response_content = "这是自定义响应"
        message = AIMessage(content=response_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

# 使用
model = MyChatModel()
result = model.invoke([HumanMessage(content="你好")])
print(result.content)  # "这是自定义响应"
```

### 5.3 BaseLLM

```python
from langchain_core.language_models import BaseLLM, LLMResult

class MyLLM(BaseLLM):
    """自定义 LLM 示例"""

    @property
    def _llm_type(self) -> str:
        return "my-llm"

    def _call(self, prompt: str, **kwargs) -> str:
        return f"响应: {prompt}"

# 使用
llm = MyLLM()
result = llm.invoke("你好")
print(result)  # "响应: 你好"
```

### 5.4 常用集成模型

```python
# OpenAI chat model
from langchain_openai import ChatOpenAI
chat_model = ChatOpenAI(model="gpt-4")

# Anthropic chat model
from langchain_anthropic import ChatAnthropic
chat_model = ChatAnthropic(model="claude-3-opus")

# 使用
result = chat_model.invoke([HumanMessage(content="Hello")])
```

### 5.5 使用场景

- **统一接口**：为不同模型提供商提供统一接口
- **自定义模型**：实现自己的模型封装
- **模型切换**：轻松切换不同的模型供应商

---

## 6. Runnable 接口与链式组合 (Runnables)

### 6.1 概述

`Runnable` 是 LangChain 的核心接口，所有组件都实现了这个接口。通过管道操作符 `|` 可以轻松组合多个组件形成处理链。

### 6.2 核心概念

LangChain Expression Language (LCEL) 是一种声明式编写生产级 LLM 程序的方法。使用 LCEL 创建的程序天生支持：
- **同步/异步操作**
- **批量处理**
- **流式输出**

### 6.3 基本使用

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 创建组件
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个幽默的助手。"),
    ("human", "{question}")
])

model = ChatOpenAI()
parser = StrOutputParser()

# 使用管道操作符组合 chain
chain = prompt | model | parser

# 调用 chain
result = chain.invoke({"question": "为什么天是蓝色的？"})
print(result)
```

### 6.4 主要 Runnable 类型

| 类型 | 说明 |
|------|------|
| `Runnable` | 基类，所有组件都继承自此 |
| `RunnableLambda` | 将普通函数转换为 Runnable |
| `RunnableParallel` | 并行执行多个 Runnable |
| `RunnableSequence` | 顺序执行多个 Runnable |
| `RunnableBranch` | 根据条件选择分支 |

### 6.5 RunnableLambda - 函数转 Runnable

```python
from langchain_core.runnables import RunnableLambda

# 将普通函数转换为 Runnable
def add_exclamation(x: str) -> str:
    return x + "!"

# 使用 RunnableLambda
chain = RunnableLambda(add_exclamation)
result = chain.invoke("Hello")
print(result)  # "Hello!"

# 带参数的函数
def multiply(x: int, y: int) -> int:
    return x * y

chain = RunnableLambda(multiply)
result = chain.invoke({"x": 5, "y": 3})
print(result)  # 15
```

### 6.6 RunnableParallel - 并行执行

```python
from langchain_core.runnables import RunnableParallel

# 创建多个独立的 runnable
chain1 = RunnableLambda(lambda x: x * 2)
chain2 = RunnableLambda(lambda x: x + 10)
chain3 = RunnableLambda(lambda x: x - 5)

# 并行执行
parallel = RunnableParallel({
    "double": chain1,
    "plus_ten": chain2,
    "minus_five": chain3
})

result = parallel.invoke(10)
print(result)  # {'double': 20, 'plus_ten': 20, 'minus_five': 5}

# 简写形式
parallel = chain1 | (chain2 + chain3)  # 不支持直接相加
```

### 6.7 RunnableBranch - 条件分支

```python
from langchain_core.runnables import RunnableBranch
from langchain_core.prompts import PromptTemplate

# 定义不同的分支
greeting_branch = RunnableBranch(
    lambda x: x.get("language") == "en",
    PromptTemplate.from_template("Hello! How can I help you?"),
    PromptTemplate.from_template("你好！有什么可以帮助你的？")
)

chain = greeting_branch | ChatOpenAI()

# 根据输入选择分支
result = chain.invoke({"language": "en"})
```

### 6.8 配置与回退

```python
from langchain_core.runnables import RunnableWithFallbacks

# 添加回退处理
chain_with_fallback = chain.with_fallbacks(
    fallbacks=[fallback_chain],
    exception_handler=lambda e: print(f"Error: {e}")
)
```

### 6.9 使用场景

- **数据处理管道**：构建复杂的数据处理流程
- **LLM 链式调用**：组合提示词、模型、输出解析器
- **条件路由**：根据输入选择不同的处理路径
- **并行处理**：同时执行多个独立任务

---

## 7. 工具 (Tools)

### 7.1 概述

工具让 AI 模型能够与外部世界交互，执行计算、查询数据或调用 API。

### 7.2 BaseTool 基础用法

```python
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel

# 定义工具的输入schema
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")

# 使用 @tool 装饰器（推荐）
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 实际应用中这里会调用天气API
    return f"{city}今天晴天，气温25度"

print(get_weather.name)        # "get_weather"
print(get_weather.description) # "获取指定城市的天气信息"
print(get__weather.args_schema) # WeatherInput

# 调用工具
result = get_weather.invoke({"city": "北京"})
print(result)  # "北京今天晴天，气温25度"
```

### 7.3 StructuredTool - 结构化工具

```python
from langchain_core.tools import StructuredTool

def calculate_bmi(weight: float, height: float) -> dict:
    """计算BMI指数"""
    bmi = weight / (height ** 2)
    return {"bmi": round(bmi, 2), "status": "正常" if 18.5 <= bmi <= 24 else "异常"}

tool = StructuredTool.from_function(
    func=calculate_bmi,
    name="calculate_bmi",
    description="根据体重(kg)和身高(m)计算BMI指数"
)

result = tool.invoke({"weight": 70, "height": 1.75})
print(result)  # {"bmi": 22.86, "status": "正常"}
```

### 7.4 将 Runnable 转换为工具

```python
from langchain_core.tools import convert_runnable_to_tool
from langchain_core.runnables import RunnableLambda

# 将任何 Runnable 转换为工具
my_runnable = RunnableLambda(lambda x: x.upper())
tool = convert_runnable_to_tool(
    my_runnable,
    name="uppercase",
    description="将输入文本转换为大写"
)
```

### 7.5 创建 Retriever 工具

```python
from langchain_core.tools import create_retriever_tool

# 从 retriever 创建工具
tool = create_retriever_tool(
    retriever=my_retriever,
    name="search_knowledge_base",
    description="搜索知识库获取相关信息"
)
```

### 7.6 使用 ToolCall 和 ToolMessage

```python
from langchain_core.messages import ToolCall, ToolMessage

# 模型生成的工具调用
tool_call = ToolCall(
    name="get_weather",
    args={"city": "上海"},
    id="call_123"
)

# 执行工具获取结果
tool_result = get_weather.invoke(tool_call.args)

# 创建工具消息
tool_msg = ToolMessage(
    content=str(tool_result),
    tool_call_id="call_123"
)
```

### 7.7 将工具绑定到模型（LLM 调用工具的核心）

这是工具系统的关键步骤 — 让模型能够**生成 tool_calls**，而不是直接执行。

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}今天晴天，气温25度"

# 创建模型并绑定工具
model = ChatOpenAI(model="gpt-4o")
model_with_tools = model.bind_tools([get_weather])

# 调用模型，模型会生成 tool_calls（不是直接执行工具）
result = model_with_tools.invoke("北京今天天气怎么样？")
print(result.content)        # '' （模型不返回文本）
print(result.tool_calls)    # [ToolCall(name='get_weather', args={'city': '北京'}, id='...')]
```

### 7.8 完整工具调用链（Agent 模式）

模型生成 `tool_call` 后，需要手动执行工具并把结果传回模型：

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    weather_data = {
        "北京": "晴天，25度",
        "上海": "雨天，22度",
        "东京": "多云，28度"
    }
    return weather_data.get(city, "未知城市")

model = ChatOpenAI(model="gpt-4o")
model_with_tools = model.bind_tools([get_weather])

# 第一步：用户输入
messages = [HumanMessage(content="北京和上海的天气如何？")]

# 第二步：模型生成 tool_call
response = model_with_tools.invoke(messages)
messages.append(response)  # 添加 AI 消息（包含 tool_calls）

print("模型生成的 tool_calls:", response.tool_calls)
# → [ToolCall(name='get_weather', args={'city': '北京'}, id='...'),
#    ToolCall(name='get_weather', args={'city': '上海'}, id='...')]

# 第三步：执行工具，生成 ToolMessage, 把工具messages添加到messages，然后再交给model去执行
for tool_call in response.tool_calls:
    tool_result = get_weather.invoke(tool_call.args)
    messages.append(ToolMessage(
        content=str(tool_result),
        tool_call_id=tool_call.id
    ))

print("执行工具后的消息列表:")
for msg in messages:
    print(f"  {msg.type}: {msg.content[:50] if hasattr(msg, 'content') else msg.tool_calls}")

# 第四步：再次调用模型，传入工具执行结果
final_response = model.invoke(messages)
print("模型最终回复:", final_response.content)
```

### 7.9 使用 bind_tools 的配置选项

```python
# 强制模型始终调用特定工具
model_with_tools = model.bind_tools([get_weather], tool_choice="get_weather")

# 允许模型选择是否调用工具（默认行为）
model_with_tools = model.bind_tools([get_weather], tool_choice="auto")

# 强制模型调用第一个工具
model_with_tools = model.bind_tools([get_weather], tool_choice="any")

# 传入一个 JSON Schema 限制参数范围
from pydantic import BaseModel

class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")
    unit: str = Field(default="celsius", description="温度单位")

model_with_tools = model.bind_tools(
    [get_weather],
    tool_choice="get_weather",
    parallel_tool_calls=False  # 禁止并行调用，改为串行
)
```

### 7.10 使用 ToolChoice 强制调用

```python
# 传入一个函数类型的 tool_choice 时，必须调用该工具
model_with_tools = model.bind_tools(
    [get_weather, get_news],
    tool_choice=get_weather  # 强制使用 get_weather
)

result = model_with_tools.invoke("随便问点什么")
print(result.tool_calls)  # 必定包含 get_weather 的调用
```

### 7.11 多个不同工具 — 模型自主选择

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}晴天，25度"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "计算错误"

@tool
def get_date() -> str:
    """获取当前日期"""
    from datetime import date
    return str(date.today())

# 绑定多个工具
model = ChatOpenAI(model="gpt-4o")
model_with_tools = model.bind_tools([get_weather, calculate, get_date])

# 模型会根据用户问题自主选择调用哪个工具
messages = [HumanMessage(content="北京今天冷吗？")]
response = model_with_tools.invoke(messages)
print("tool_calls:", response.tool_calls)
# → [ToolCall(name='get_weather', args={'city': '北京'}, id='...')]

# 另一个问题
messages = [HumanMessage(content="123 * 456 等于多少？")]
response = model_with_tools.invoke(messages)
print("tool_calls:", response.tool_calls)
# → [ToolCall(name='calculate', args={'expression': '123 * 456'}, id='...')]

# 再问日期
messages = [HumanMessage(content="今天是几号？")]
response = model_with_tools.invoke(messages)
print("tool_calls:", response.tool_calls)
# → [ToolCall(name='get_date', args={}, id='...')]
```

### 7.12 多个工具 + 完整调用链

```python
def run_multi_tool_agent(user_question: str, tools: list, model) -> str:
    """完整的多工具 Agent 循环"""
    model_with_tools = model.bind_tools(tools)

    messages = [HumanMessage(content=user_question)]

    # Agent 循环：模型决定是否调用工具
    max_turns = 5
    for _ in range(max_turns):
        response = model_with_tools.invoke(messages)

        # 没有 tool_calls，说明模型直接回复了
        if not response.tool_calls:
            return response.content

        messages.append(response)

        # 执行所有 tool_calls
        for tool_call in response.tool_calls:
            # 找到对应的工具
            matched_tool = next(t for t in tools if t.name == tool_call.name)
            result = matched_tool.invoke(tool_call.args)
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call.id
            ))

    return "已达到最大循环次数"

# 使用
tools = [get_weather, calculate, get_date]
result = run_multi_tool_agent("北京天气怎么样？123加456等于多少？", tools, model)
print(result)
# 模型会并行调用 get_weather 和 calculate（如果支持）
```

### 7.13 parallel_tool_calls 参数

```python
# 默认：模型可能并行调用多个工具
model_with_tools = model.bind_tools([get_weather, calculate])
response = model_with_tools.invoke("北京天气和123*456的结果")
print(len(response.tool_calls))  # 可能返回 2（两个工具都调用）

# 禁止并行：模型必须逐个调用
model_with_tools = model.bind_tools(
    [get_weather, calculate],
    parallel_tool_calls=False
)
response = model_with_tools.invoke("北京天气和123*456的结果")
print(len(response.tool_calls))  # 最多 1，需要等上一个结果再调用下一个
```

### 7.14 使用场景

- **函数调用**：让 AI 调用外部函数获取信息
- **API 集成**：连接外部服务和 API
- **计算任务**：执行复杂计算
- **数据检索**：从数据库或知识库检索信息

---

## 8. 内存 (Memory)

### 8.1 概述

内存组件用于在对话过程中存储和检索历史消息。

### 8.2 BaseChatMessageHistory

```python
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# 使用内存聊天历史
chat_history = InMemoryChatMessageHistory()

# 添加消息
chat_history.add_user_message("你好！")
chat_history.add_ai_message("你好，有什么可以帮助你的吗？")

# 获取所有消息
messages = chat_history.messages
for msg in messages:
    print(f"{msg.type}: {msg.content}")

# 清空历史
chat_history.clear()
```

### 8.3 自定义聊天历史存储

```python
import json
import os
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import messages_to_dict, messages_from_dict

class FileChatMessageHistory(BaseChatMessageHistory):
    """基于文件的聊天历史存储"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    @property
    def messages(self) -> list:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r") as f:
            data = json.load(f)
        return messages_from_dict(data)

    def add_messages(self, messages) -> None:
        existing = self.messages
        existing.extend(messages)
        with open(self.file_path, "w") as f:
            #dump就是将dict转化为json，当然也有dumps将dict转化为json
            json.dump(messages_to_dict(existing), f)

    def clear(self) -> None:
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

# 使用
history = FileChatMessageHistory("chat_history.json")
history.add_user_message("你好")
history.add_ai_message("你好！")
```

### 8.4 RunnableWithMessageHistory

```python
from langchain_core.runnables.history import RunnableWithMessageHistory

# 创建带历史记录的 chain
chain = prompt | model | parser

# 包装为带历史记录的版本
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history= lambda session_id: InMemoryChatMessageHistory(),
    input_messages_key="question",
    history_messages_key="chat_history"
)

# 调用（需要提供 session_id）
result = chain_with_history.invoke(
    {"question": "我叫张三"},
    config={"configurable": {"session_id": "user_123"}}
)
```

### 8.5 使用场景

- **多轮对话**：维护对话上下文
- **会话管理**：持久化用户会话
- **上下文增强**：为模型提供历史信息

---

## 9. 回调 (Callbacks)

### 9.1 概述

回调处理器用于监听 LangChain 执行过程中的事件，便于日志记录、监控和调试。

### 9.2 BaseCallbackHandler

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.outputs import LLMResult

class MyCallbackHandler(BaseCallbackHandler):
    """自定义回调处理器"""

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM 开始处理，提示词数量: {len(prompts)}")

    def on_llm_end(self, response: LLMResult, **kwargs):
        print(f"LLM 处理完成，响应: {response}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"Chain 开始执行")

    def on_chain_end(self, outputs, **kwargs):
        print(f"Chain 执行完成，输出: {outputs}")

    def on_tool_start(self, serialized, inputs, **kwargs):
        tool_name = serialized.get("name", "unknown")
        print(f"工具 {tool_name} 开始执行")

    def on_tool_end(self, output, **kwargs):
        print(f"工具执行完成，结果: {output}")

    def on_retriever_start(self, serialized, query, **kwargs):
        print(f"检索器开始查询: {query}")

    def on_retriever_end(self, documents, **kwargs):
        print(f"检索完成，找到 {len(documents)} 个文档")
```

### 9.3 使用回调

```python
from langchain_core.callbacks import StdOutCallbackHandler

# 创建 handler
handler = StdOutCallbackHandler()

# 在 chain 中使用
chain = prompt | model | parser

result = chain.invoke(
    {"question": "你好"},
    config={"callbacks": [handler]}
)

# 使用 CallbackManager
from langchain_core.callbacks.manager import CallbackManager
callback_manager = CallbackManager(handlers=[handler])
result = chain.invoke(
    {"question": "你好"},
    config={"callbacks": callback_manager}
)
```

### 9.4 常用内置 Handler

| Handler | 说明 |
|---------|------|
| `StdOutCallbackHandler` | 输出到标准输出 |
| `StreamingStdOutCallbackHandler` | 流式输出到标准输出 |
| `FileCallbackHandler` | 输出到文件 |
| `UsageMetadataCallbackHandler` | 记录 token 使用量 |

### 9.5 使用场景

- **日志记录**：追踪执行过程
- **性能监控**：测量各阶段耗时
- **调试开发**：查看中间输出
- **成本追踪**：记录 token 使用量

---

## 10. 文档 (Documents)

### 10.1 概述

`Document` 类用于表示文本文档，是 RAG（检索增强生成）系统的基本单元。

### 10.2 Document 类

```python
from langchain_core.documents import Document

# 创建文档
doc = Document(
    page_content="这是文档的内容文本。",
    metadata={
        "source": "example.txt",
        "page": 1,
        "author": "张三"
    }
)

print(doc.page_content)  # "这是文档的内容文本。"
print(doc.metadata)       # {"source": "example.txt", "page": 1, "author": "张三"}
```

### 10.3 BaseDocumentTransformer

```python
from langchain_core.documents import Document, BaseDocumentTransformer
from typing import List

class ChunkingTransformer(BaseDocumentTransformer):
    """自定义文档分块处理器"""

    def __init__(self, chunk_size: int = 100):
        self.chunk_size = chunk_size

    def transform_documents(
        self,
        documents: List[Document],
        **kwargs
    ) -> List[Document]:
        """将文档分块"""
        chunks = []
        for doc in documents:
            text = doc.page_content
            for i in range(0, len(text), self.chunk_size):
                chunk_text = text[i:i + self.chunk_size]
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata=doc.metadata.copy()
                ))
        return chunks

    async def atransform_documents(
        self,
        documents: List[Document],
        **kwargs
    ) -> List[Document]:
        return self.transform_documents(documents)

# 使用
transformer = ChunkingTransformer(chunk_size=50)
long_doc = Document(page_content="A" * 200, metadata={"source": "test"})
chunks = transformer.transform_documents([long_doc])
print(len(chunks))  # 4
```

### 10.4 BaseDocumentCompressor

```python
from langchain_core.documents import Document, BaseDocumentCompressor

class RelevanceCompressor(BaseDocumentCompressor):
    """根据相关性过滤文档"""

    def compress_documents(
        self,
        documents: List[Document],
        query: str,
        **kwargs
    ) -> List[Document]:
        """只保留包含查询关键词的文档"""
        keywords = set(query.lower().split())
        filtered = []
        for doc in documents:
            if any(word in doc.page_content.lower() for word in keywords):
                filtered.append(doc)
        return filtered
```

### 10.5 使用场景

- **文档分块**：将长文档分割成小块
- **文档压缩**：过滤不相关的文档
- **RAG 系统**：构建检索增强生成管道
- **知识库**：存储和检索文档

---

## 11. 检索器 (Retrievers)

### 11.1 概述

检索器根据查询返回相关的 `Document` 对象，是 RAG 系统的核心组件。

### 11.2 BaseRetriever

```python
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from typing import List

class SimpleRetriever(BaseRetriever):
    """简单的关键词匹配检索器"""

    def __init__(self, documents: List[Document]):
        self.documents = documents

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None
    ) -> List[Document]:
        """根据关键词匹配返回相关文档"""
        query_words = set(query.lower().split())
        relevant = []
        for doc in self.documents:
            doc_words = set(doc.page_content.lower().split())
            if query_words & doc_words:  # 有交集
                relevant.append(doc)
        return relevant

# 使用
docs = [
    Document(page_content="Python 是一种编程语言", metadata={"id": "1"}),
    Document(page_content="JavaScript 用于 Web 开发", metadata={"id": "2"}),
    Document(page_content="Python 可用于数据分析", metadata={"id": "3"})
]

retriever = SimpleRetriever(docs)
results = retriever.invoke("Python")
print(len(results))  # 2
for doc in results:
    print(doc.page_content)
```

### 11.3 异步检索器

```python
class AsyncRetriever(BaseRetriever):
    """异步检索器示例"""

    def __init__(self, documents: List[Document]):
        self.documents = documents

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None
    ) -> List[Document]:
        # 同步实现
        return [doc for doc in self.documents if query in doc.page_content]

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None
    ) -> List[Document]:
        # 异步实现
        import asyncio
        await asyncio.sleep(0.1)  # 模拟异步操作
        return self._get_relevant_documents(query)
```

### 11.4 在 Chain 中使用

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 创建 RAG chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "基于以下上下文回答问题。\n\n{context}"),
    ("human", "{question}")
])

rag_chain = (
    {
        "context": retriever | (lambda docs: "\n".join([d.page_content for d in docs])),
        "question": RunnablePassthrough()
    }
    | prompt
    | model
    | StrOutputParser()
)

# 调用
result = rag_chain.invoke("Python 有什么用？")
```

### 11.5 使用场景

- **RAG 系统**：检索增强生成
- **知识库问答**：从文档库中检索相关信息
- **语义搜索**：基于向量相似度的检索
- **混合检索**：结合关键词和语义检索

---

## 12. 总结

`langchain_core` 提供了构建 LLM 应用所需的所有核心抽象：

| 模块 | 核心组件 | 用途 |
|------|---------|------|
| **Messages** | HumanMessage, AIMessage, SystemMessage | 对话消息表示 |
| **Prompts** | ChatPromptTemplate, PromptTemplate | 动态提示构建 |
| **Output Parsers** | JsonOutputParser, StrOutputParser | 结构化输出解析 |
| **Models** | BaseChatModel, BaseLLM | 模型接口抽象 |
| **Runnables** | Runnable, chain (`\|`) | 组件组合 |
| **Tools** | BaseTool, tool | 外部功能调用 |
| **Memory** | BaseChatMessageHistory | 对话历史管理 |
| **Callbacks** | BaseCallbackHandler | 事件监听与监控 |
| **Documents** | Document | 文档表示 |
| **Retrievers** | BaseRetriever | 信息检索 |

这些组件共同构成了 LangChain 生态系统的基础，通过模块化和可组合的设计，让开发者能够灵活构建各种 LLM 应用。

---

## 参考资源

- [LangChain Core 官方文档](https://docs.langchain.com/oss/python/langchain_core/)
- [API 参考](https://reference.langchain.com/python/langchain_core/)
- [LangChain 官网](https://docs.langchain.com/)
