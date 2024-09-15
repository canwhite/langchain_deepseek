from langchain.chains import RetrievalQA #检索QA链，在文档上进行检索
from langchain_community.document_loaders import CSVLoader #文档加载器，采用csv格式存储
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.indexes import VectorstoreIndexCreator #导入向量存储索引创建器
from langchain_huggingface import HuggingFaceEmbeddings
from tool import llm ,get_completion
from langchain.prompts import ChatPromptTemplate

# #加载中文数据
file = 'docs/product_data.csv'
loader = CSVLoader(file_path=file)
data = loader.load()

# #查看数据
# import pandas as pd
# test_data = pd.read_csv(file,skiprows=0)


# 这个方法的作用是创建一个向量存储索引，用于存储和检索文档。
# 具体步骤如下：
# 1. 使用CSVLoader加载CSV文件中的数据。
# 2. 使用VectorstoreIndexCreator创建一个向量存储索引。
# 3. 指定向量存储类为DocArrayInMemorySearch，并使用HuggingFaceEmbeddings进行嵌入。
# 4. 从加载器中调用，通过文档加载器列表加载数据。
# 5. 最终生成一个向量存储索引，可以用于后续的文档检索和查询。

index = VectorstoreIndexCreator(
    vectorstore_cls=DocArrayInMemorySearch,
    embedding=HuggingFaceEmbeddings()
).from_loaders([loader])


#拿到qa
qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=index.vectorstore.as_retriever(), 
    verbose=True,
    # chain_type_kwargs 是一个字典，用于传递给链类型的额外参数。
    # 在这个例子中，它被用来指定文档之间的分隔符。
    # 具体来说，"document_separator": "<<<<>>>>>" 表示在文档之间插入 "<<<<>>>>>" 作为分隔符。
    # 这有助于在处理多个文档时，模型能够识别文档的边界。
    chain_type_kwargs = {
        "document_separator": "<<<<>>>>>"
    }
)

print(data[1])

#确保data[1]是一个字符串
query = data[1].page_content if hasattr(data[1], 'page_content') else str(data[1])



res = qa.run(f"{query} 请求结果请转化为中文")
print(res)