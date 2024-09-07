'''
# （嵌入）是一种将类别数据，如单词、句子或者整个文档，转化为实数向量的技术
我们可以使用词嵌入（word embeddings）来表示文本数据。
在词嵌入中，每个单词被转换为一个向量，这个向量捕获了这个单词的语义信息。
例如，"king" 和 "queen" 这两个单词在嵌入空间中的位置将会非常接近，因为它们的含义相似。
而 "apple" 和 "orange" 也会很接近，因为它们都是水果。
而 "king" 和 "apple" 这两个单词在嵌入空间中的距离就会比较远，因为它们的含义不同


----HuggingFaceEmbeddings VS OpenAIEmbedding----

HuggingFaceEmbedding:

用户可以直接从 Hugging Face 的模型库中加载模型，进行本地推理。
支持离线使用，不需要依赖网络连接。

OpenAIEmbedding:
需要通过 OpenAI 的 API 进行调用，依赖网络连接。
用户需要注册 OpenAI 的 API 密钥，并通过 API 请求获取嵌入结果。

'''
# from langchain.embeddings.openai import OpenAIEmbeddings # need open ai id
from langchain_huggingface import HuggingFaceEmbeddings


embedding = HuggingFaceEmbeddings()