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


API_KEY=  os.getenv("DEEPSEEK_KEY")
BASE_URL = "https://api.deepseek.com"


class SingletonChatOpenAI:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonChatOpenAI, cls).__new__(cls)
            cls._instance.llm = ChatOpenAI(
                model='deepseek-chat', 
                openai_api_key=API_KEY, 
                openai_api_base=BASE_URL,
                max_tokens=1024
            )
        return cls._instance

    def __getattr__(self, name):
        return getattr(self._instance.llm, name)

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



# 5) 检索问答链，可以取代第四步，开始直接问问题了
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb_chinese.as_retriever()
)

# 可以以该方式进行检索问答
question = "这节课的主要话题是什么"
result = qa_chain.invoke({"query": question})

print(result["result"])