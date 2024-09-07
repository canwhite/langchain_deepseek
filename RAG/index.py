from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings # need open ai id
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
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
    chunk_size = 1000,  # 每个文本块的大小。这意味着每次切分文本时，会尽量使每个块包含 1500 个字符。
    chunk_overlap = 150  # 每个文本块之间的重叠部分。
)

splits = text_splitter.split_documents(docs)

print("--splits lenght--",len(splits))
# 3）嵌入，实际上做的事情是：将每个文本块转换为向量
# PS： 这里我们换成了hugging face的embedding，因为它免费，离线
embedding = HuggingFaceEmbeddings()

persist_directory_chinese = 'docs/chroma/matplotlib/'

# 4）存储
# 4.1）创建向量存储

#注意不会重复创建
vectordb_chinese = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory=persist_directory_chinese  # 允许我们将persist_directory目录保存到磁盘上
)


print("db collection count",vectordb_chinese._collection.count())

# 4.2）相似性搜索
question_chinese = "Matplotlib是什么？"

# k=3 表示在相似性搜索中返回最相关的3个文档
docs_chinese = vectordb_chinese.similarity_search(question_chinese,k=3)

for doc_chinese in docs_chinese:
    print(doc_chinese.metadata,doc_chinese.page_content)

# print(docs_chinese[0].page_content)

# 4.3）持久化, 现在已经是自动化的了
# vectordb_chinese.persist()





