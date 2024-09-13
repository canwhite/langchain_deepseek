from langchain.chains import RetrievalQA  #检索QA链，在文档上进行检索
from langchain_community.document_loaders import CSVLoader #文档加载器，采用csv格式存储
from langchain_community.vectorstores import DocArrayInMemorySearch
from IPython.display import display, Markdown #在jupyter显示信息的工具
import pandas as pd
from tool import llm ,get_completion
#导入向量存储索引创建器
from langchain.indexes import VectorstoreIndexCreator 
from langchain_huggingface import HuggingFaceEmbeddings
# prompts template 
from langchain.prompts import ChatPromptTemplate


file = "docs/OutdoorClothingCatalog_1000.csv"

#使用langchain加载器对数据进行导入
loader = CSVLoader(file_path=file)

docs = loader.load()

#TODO，这里应该有个拆分，但是我们的文件太小，这里就不做了

# 使用pandas导入数据，用以查看
# data = pd.read_csv(file,usecols=[1, 2])
# data.head()

embeddings = HuggingFaceEmbeddings()

# embedding的一些属性
embed = embeddings.embed_query("你好呀，我的名字叫小可爱")

#查看得到向量表征的长度
print("\n\033[32m向量表征的长度: \033[0m \n", len(embed))

#每个元素都是不同的数字值，组合起来就是文本的向量表征
print("\n\033[32m向量表征前5个元素: \033[0m \n", embed[:5])

# 创建指定向量存储类, 创建完成后，从加载器中调用, 通过文档加载器列表加载
db =  DocArrayInMemorySearch.from_documents(docs, embeddings)


query = "请推荐一件具有防晒功能的衬衫"
#使用上面的向量存储来查找与传入查询类似的文本，得到一个相似文档列表
docs = db.similarity_search(query)

# 合并获得的相似文档内容
#合并获得的相似文档内容
qdocs = "".join([docs[i].page_content for i in range(len(docs))])  

'''
# 使用查询结果作为提示词，向模型询问
# call_as_llm 是一个用于调用语言模型的方法。它通常用于将输入文本传递给语言模型并获取模型的响应。
# 示例代码
# response = llm.call_as_llm(f"{qdocs}问题：请用markdown表格的方式列出所有具有防晒功能的衬衫，对每件衬衫描述进行总结")

prompts = f"{qdocs}问题：请用markdown表格的方式列出所有具有防晒功能的衬衫，对每件衬衫描述进行总结"
prompts_template = ChatPromptTemplate.from_template(prompts)

messages = prompts_template.format_messages(qdocs=qdocs);
response = get_completion(messages)

print(response)
'''
# 使用检索问答链来回答查询
#基于向量储存，创建检索器
retriever = db.as_retriever() 

'''
# from_chain_type 和 from_llm 的区别：
# from_chain_type 是用于创建检索问答链的函数，它允许你指定链的类型（如 "stuff"、"map_reduce" 等）。
# from_llm 是用于创建基于语言模型的链的函数，它允许你指定使用的语言模型。

# 除了 "stuff" 之外的其他链类型及其含义：
# 1. "map_reduce": 首先对每个文档进行独立处理，然后将所有文档的结果合并。
# 2. "refine": 逐步改进答案，首先生成一个初始答案，然后根据每个文档逐步改进。
# 3. "map_rerank": 对每个文档进行独立处理，并根据相关性评分重新排序结果。
# 4. "stuff": 将所有文档一次性传递给模型进行处理。

# 示例代码：
# 使用 "map_reduce" 链类型
qa_map_reduce = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="map_reduce", 
    retriever=retriever, 
    verbose=True
)

# 使用 "refine" 链类型
qa_refine = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="refine", 
    retriever=retriever, 
    verbose=True
)

# 使用 "map_rerank" 链类型
qa_map_rerank = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="map_rerank", 
    retriever=retriever, 
    verbose=True
)
'''

qa_stuff = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=retriever, 
    verbose=True
)

#创建一个查询并在此查询上运行链
query =  "请用markdown表格的方式列出所有具有防晒功能的衬衫，对每件衬衫描述进行总结"

response = qa_stuff.run(query)
print(response)