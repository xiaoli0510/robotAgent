import logging
import os
from datetime import datetime

from utils.path_tool import get_abs_path

LOG_ROOT = get_abs_path("logs")

#确保logs文件夹存在，如果不存在会自动创建
os.makedirs(LOG_ROOT, exist_ok=True)

#日志的格式配置
DEFAULT_LOG_FORMAT = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")

def get_logger(
        name:str = "agent",
        console_level:int = logging.INFO, #控制台的级别
        file_level:int  = logging.DEBUG,#文件级别
        log_file=None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加，保证后面的代码只执行一次
    if logger.handlers:
        return logger

    #添加控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    #添加文件Handler
    if not  log_file:
        #日志文件的存放路径
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger

#快捷获取日志器
logger = get_logger()
