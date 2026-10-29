from langchain.agents import create_agent

from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import rag_summarize, get_weather, get_user_id, get_user_location, get_current_month,fetch_external_data,fill_context_for_report
from agent.tools.middleware import monitor_tool,log_before_model,report_prompt_switch

class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, get_weather, get_user_id, get_user_location, get_current_month,fetch_external_data,fill_context_for_report],
            middleware = [monitor_tool,log_before_model,report_prompt_switch]
        )

    def execute_stream(self, query: str):
        input_dirt = {
            "messages": [
                {"role": "user", "content":query}
            ]
        }

        # 返回迭代器
        for chunk in self.agent.stream(input_dirt,stream_mode="values", context={"reoort": False}):
            latest_message = chunk["messages"][-1]
            if latest_message:
                yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("生成我的个人的使用报告"):
        print(chunk, end="", flush =True)