from langchain.text_splitter import RecursiveCharacterTextSplitter

#首先要理解，有各种各样的加载器视频、文本、pef and so on，我们这里主要讲pdf的加载器
#0）加载单个
loader = PyPDFLoader("docs/第一回：Matplotlib初相识.pdf")
documents = loader.load()


# 1）批量加载 PDF
loaders_chinese = [
    # 故意添加重复文档，使数据混乱
    PyPDFLoader("docs/第一回：Matplotlib初相识.pdf"),
    PyPDFLoader("docs/第二回：艺术画笔见乾坤.pdf"),
    PyPDFLoader("docs/第三回：布局格式定方圆.pdf")
]
docs = []
for loader in loaders_chinese:
    docs.extend(loader.load())
