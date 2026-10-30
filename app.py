"""
1. title
2. 用户输入
3. agent回复，流式输出
4. 持久化问题的解决
"""
import streamlit as st
import time
from agent.react_agent import ReactAgent

st.title("智扫通机器人智能客服")
st.divider()

# 避免页面元素改变时创建agent
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

# 遍历输出message
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])
# 用户输入提示词
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({
            "role":"user",
            "content":prompt
        })

    response_messages = []
    with st.spinner("智能客服思考中..."):
        # 调用agent的流式输出
        res_stream = st.session_state["agent"].execute_stream(prompt)

        # 因为迭代器消耗了就没有了,capture是在原样返回迭代器的情况下，将数据添加到cache_list
        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    # chunk的字符打印效果
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write(capture(res_stream, response_messages))
        st.session_state["message"].append({
            "role":"assistant",
            "content":response_messages[-1]
        })
        # 每次完成一轮对话后，重新跑一次，去掉ai的思考过程，页面只保留最后的答案即可，st.session_state["message"]里面记录的也是最后的答案
        # 强制刷新当前页面
        st.rerun()