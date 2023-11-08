from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.chains.llm import LLMChain
from langchain.tools import PythonREPLTool
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from decouple import config
import os

from custom_classes import CustomOutputParser, CustomPromptTemplate
from config import data_analyzer_prompt_template


os.environ["OPENAI_API_TYPE"] = config("OPENAI_API_TYPE")
os.environ["OPENAI_API_BASE"] = config("OPENAI_API_BASE")
os.environ["OPENAI_API_VERSION"] = config("OPENAI_API_VERSION")
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")


def create_agent(temperature, file_path):
    llm_chat_model = AzureChatOpenAI(deployment_name="gpt-4", temperature=temperature)
    python_tool = PythonREPLTool()
    tools = [python_tool]
    tool_names = [tool.name for tool in tools]
    prompt = CustomPromptTemplate(
        template=data_analyzer_prompt_template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps", "history", "file_path"],
    )
    output_parser = CustomOutputParser()
    llm_chain = LLMChain(llm=llm_chat_model, prompt=prompt)
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names,
    )
    memory = ConversationBufferWindowMemory(
        memory_key="history",
        k=10,
        return_messages=True,
        output_key="output",
        input_key="input",
    )

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        return_intermediate_steps=True,
    )
    return agent_executor
