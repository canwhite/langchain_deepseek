from langchain.chains import RetrievalQA #检索QA链，在文档上进行检索
from langchain_community.document_loaders import CSVLoader #文档加载器，采用csv格式存储
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.indexes import VectorstoreIndexCreator #导入向量存储索引创建器
from langchain_huggingface import HuggingFaceEmbeddings
from tool import llm ,get_completion
from langchain.prompts import ChatPromptTemplate
import os
# 设置环境变量以避免 tokenizers 警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

'''
===========================section1: 创建llm=========================
'''

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


examples = [
    {
        "query": "Do the Cozy Comfort Pullover Set have side pockets?",
        "answer": "Yes"
    },
    {
        "query": "What collection is the Ultra-Lofty 850 Stretch Down Hooded Jacket from?",
        "answer": "The DownTek collection"
    }
]



'''
=============================setction2: 人工比较============================
'''

from langchain.evaluation.qa import QAGenerateChain #导入QA生成链，它将接收文档，并从每个文档中创建一个问题答案对
import langchain

'''
example_gen_chain = QAGenerateChain.from_llm(llm)
#为所有不同的示例创建预测
new_examples = example_gen_chain.apply([{"doc": t} for t in data[:5]]) 

#查看用例数据
examples += [ v for item in new_examples for k,v in item.items()]
print(examples);

langchain.debug = True

qa.run(examples[0]["query"])

langchain.debug = False

'''


'''
=============================setction3: 自动比较============================
'''

# 对预测的结果进行评估，导入QA问题回答，评估链，通过语言模型创建此链
from langchain.evaluation.qa import QAEvalChain #导入QA问题回答，评估链


langchain.debug = False
#为所有不同的示例创建预测
predictions = qa.apply(examples) 

#通过调用chatGPT进行评估
# llm = ChatOpenAI(temperature=0)
eval_chain = QAEvalChain.from_llm(llm)

#在此链上调用evaluate，进行评估
graded_outputs = eval_chain.evaluate(examples, predictions)

#我们将传入示例和预测，得到一堆分级输出，循环遍历它们打印答案
for i, eg in enumerate(examples):
    print(f"Example {i}:")
    print("Question: " + predictions[i]['query'])
    #一个是真实结果，一个是预测结果
    print("Real Answer: " + predictions[i]['answer'])
    print("Predicted Answer: " + predictions[i]['result'])
    #打印最终的评价
    print("Predicted Grade: " + graded_outputs[i]['results'])
    print()