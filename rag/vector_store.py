import os

from langchain_chroma import Chroma
from langchain_core.documents import Document

from utils.config_handler import chroma_config
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.file_handler import txt_loader, pdf_loader, listdir_with_allowed_type,get_file_md5_hex
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


"""
class思路：
1. vector_store向量库
2. spliter 分割器

"""


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name = chroma_config["collection_name"],
            embedding_function = embed_model,
            persist_directory = chroma_config["persist_directory"]
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = chroma_config["chunk_size"],
            chunk_overlap = chroma_config["chunk_overlap"],
            separators=chroma_config["separators"],
            length_function = len,
        )

    # 获取检索器
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    """
   思路：
    1. 检查md5.txt中是否存在，去重。不存在则添加到md5.txt
    2. 根据path获取文件的documents
    3. 使用spliter分割documents,存入向量库
    """
    def load_document(self):
        """
        从数据文件夹内读取数据文件，并转为向量存储到向量库中
        需要计算文件的md5去重
        :return:None
        """

        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_config["md5_hex_store"])):
                #不存在md5文件,就创建文件
                open(get_abs_path(chroma_config["md5_hex_store"]), "w", encoding="utf-8").close()
                return False

            with open(get_abs_path(chroma_config["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True

                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path:str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path,"123456")

            return []

        # 获取到data下面的txt pdf文件
        allowed_files_path:list[str] = listdir_with_allowed_type(get_abs_path(chroma_config["data_path"]), tuple(chroma_config["allow_knowledge_file_type"]))

        for path in allowed_files_path:
            #获取文件的md5
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                #已经存在
                logger.info(f"[加载知识库]{path}内容已经存在知识库中，跳过")
                continue

            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                split_document:list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue

                #将内容存入向量库中
                self.vector_store.add_documents(split_document)

                #存入md5
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path} 内容加载成功")

            except Exception as e:
                # exc_info为True会记录详细的报错堆栈，False记录报错信息本身
                logger.error(f"[加载知识库]{path}加载失败,{str(e)}", exc_info=True)
                continue

# if __name__ == '__main__':
#     vs = VectorStoreService()
#     vs.load_document()
#
#     retrieve = vs.get_retriever()
#     res = retrieve.invoke('迷路了')