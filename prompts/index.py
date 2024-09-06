from langchain.prompts.chat import ChatPromptTemplate

''' 
提示词模版
'''

# 设置参数
system_template = "你当前是一个翻译助手，请将 {input_language} 翻译成 {output_language}."

human_template = "翻译内容：{text}"

# 组合
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", human_template),
])

# 传入参数
text = "Babylon是一个开源的JavaScript解析器和代码转换工具，用于分析和转换JavaScript代码。"
messages  = chat_prompt.format_messages(input_language="中文", output_language="英文", text=text)
print(messages)
print("---------")
print(messages[0].content)