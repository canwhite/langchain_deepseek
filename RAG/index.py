from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings # need open ai id
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# 自查询检索器
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
# llm 
from langchain_openai import ChatOpenAI
import os
# 导入检索式问答链
from langchain.chains import RetrievalQA
# 模版检索问答
from langchain.prompts import PromptTemplate # 中文版
# 添加记忆功能
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

import sys
import os 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_ds import SingletonChatOpenAI

# 设置环境变量以避免 tokenizers 警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

llm = SingletonChatOpenAI().llm

# 1）加载 PDF
loaders_chinese = [
    # 故意添加重复文档，使数据混乱
    PyPDFLoader("docs/第一回：Matplotlib初相识.pdf"),
    PyPDFLoader("docs/第二回：艺术画笔见乾坤.pdf"),
    PyPDFLoader("docs/第三回：布局格式定方圆.pdf")
]
docs = []
for loader in loaders_chinese:
    docs.extend(loader.load())


# 2）分割文本
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1500,  # 每个文本块的大小。这意味着每次切分文本时，会尽量使每个块包含 1500 个字符。
    chunk_overlap = 150  # 每个文本块之间的重叠部分。
)

splits = text_splitter.split_documents(docs)


# 3）嵌入，实际上做的事情是：将每个文本块转换为向量
# PS： 这里我们换成了hugging face的embedding，因为它免费，离线
embedding = HuggingFaceEmbeddings()

persist_directory_chinese = 'docs/chroma/matplotlib/'


# 4）存储
# 4.1）创建向量存储
# 检查是否已经存在相同的存储目录
if os.path.exists(persist_directory_chinese):
    vectordb_chinese = Chroma(persist_directory=persist_directory_chinese, embedding_function=embedding)
else:
    # 注意不会重复创建
    vectordb_chinese = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=persist_directory_chinese  # 允许我们将persist_directory目录保存到磁盘上
    )

print("db collection count",vectordb_chinese._collection.count())


# 4.2）相似性搜索
'''
# question_chinese = "Matplotlib是什么？"
question_chinese = "他们在第二讲中对Figure说了些什么？" #解决特殊性，比如问的是第二节的内容


#可以使用 MMR 得到不一样的结果。
#它把搜索结果中相似度很高的文档做了过滤，所以它保留了结果的相关性又同时兼顾了结果的多样性。
docs_chinese = vectordb_chinese.max_marginal_relevance_search(
    question_chinese,
    k=3,
    # filter={"source":"docs/第二回：艺术画笔见乾坤.pdf"}
)
#[]不是一个具有 is_empty 方法的对象
# if not docs_chinese:
#     docs_chinese = vectordb_chinese.similarity_search(question_chinese,k=3,filter={"source":"docs/第二回：艺术画笔见乾坤.pdf"})


# print("--0--",docs_chinese[0].page_content[:100])
# print("--1--",docs_chinese[1].page_content[:100])

'''

# 5) 检索问答链，可以取代第4-2，开始直接问问题了
# 5-1）普通检索问答链
'''
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb_chinese.as_retriever()
)
'''

# 5-2） 基于模版的检索问答链
# Build prompt

retriever=vectordb_chinese.as_retriever() # 寻回犬
'''
# 限定条件 
template = """
使用以下上下文片段来回答最后的问题。
如果你不知道答案，只需说不知道，不要试图编造答案。
答案最多使用十个句子。尽量简明扼要地回答。在回答的最后一定要说"感谢您的提问！"
{context}
问题：{question}
有用的回答："""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    memory=memory # 添加记忆功能
) 
# 可以以该方式进行检索问答
question = "这节课的主要话题是什么"
# invoke是调用的意思
result = qa_chain.invoke({"query": question})
print(result["result"])

'''
# 5-3） 添加记忆系统，memory
memory = ConversationBufferMemory(
    memory_key="chat_history", # 与 prompt 的输入变量保持一致。
    return_messages=True # 将以消息列表的形式返回聊天记录，而不是单个字符串
)

# 会默认执行基于map-reduce的检索问答链
qa = ConversationalRetrievalChain.from_llm(
    llm,
    retriever=retriever,
    memory=memory,
)
question = "这门课需要python吗？"
result = qa({"question": question})
print(result['answer'])

