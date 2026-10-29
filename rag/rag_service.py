from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


"""
思路：
通过chain.invoke实现业务
基于向量存储检索器获取到检索的文档，再将文档+query给model
"""
class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()   #向量存储，后续需要用到他的检索器
        self.retriever = self.vector_store.get_retriever() #检索文档的时候需要用到
        self.prompt_text = load_rag_prompts() #加载rag_summarize.txt的文本
        self.prompt_template = PromptTemplate.from_template(self.prompt_text) #将文本转换为提示词模板
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def retriever_docs(self,query:str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query:str) -> str:
        context_docs = self.retriever_docs(query)

        context=""
        counter = 0
        for doc in context_docs:
            counter +=1
            context += f"【参考资料{counter}】,资料{doc.page_content}, 参考元数据{doc.metadata}\n"

        return self.chain.invoke({
            "input": query,
            "context": context,
        })

if __name__ == '__main__':
    rag = RagSummarizeService()
    print(rag.rag_summarize("小户型适合哪种类型的扫地机器人"))