import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from chains.law_vector_chain import law_vector_chain
from chains.judgement_vector_chain import judgment_vector_chain
from chains.cypher_chain import judgement_cypher_chain

from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, StructuredTool

from pydantic import BaseModel
class GraphToolInput(BaseModel):
    query: str

model = AzureAIChatCompletionsModel()



tools = [
    # Tool(
    #     name="Judgment",
    #     func=judgment_vector_chain.invoke,
    #     description="""
    #         อธิบายช่วยเหลือ การให้ข้อมูล ความรู้ แนะนำ โดนใช้ข้อมูลเกี่ยวข้องกับคำพิพากษาหรือกรณีศึกษาในหัวข้อเดียวกันหรือมีความคล้ายคลึงกับ ระบุหัวข้อ เช่น การเช่าซื้อรถยนต์ การทำสัญญา
    #         โดยเน้นการระบุข้อมูลสำคัญ เช่น ประเด็นข้อพิพาท (Issue), กฎหมายที่เกี่ยวข้อง (R_Law), วิธีการดำเนินคดี (Operation)
    #         และผลคำพิพากษา (Penalty) เพื่อนำข้อมูลที่ได้มาวิเคราะห์ เปรียบเทียบ และสร้างคำตอบที่ครอบคลุมและสอดคล้องกับประเด็นที่ต้องการศึกษา
    #         ตอบกลับเป็นภาษาไทยแบบชาวบ้านใช้คุยกันเท่านั้น
    #     """,
    # ),
    # Tool(
    #     name="Law",
    #     func=law_vector_chain.invoke,
    #     description="""
    #         อธิบายช่วยเหลือ การให้ข้อมูล ความรู้ แนะนำ เกี่ยวข้องกับข้อมูลทางกฎหมาย และสร้างคำตอบที่ครอบคลุมและสอดคล้องกับประเด็นที่ต้องการศึกษา
    #         ตอบกลับเป็นภาษาไทยแบบชาวบ้านใช้คุยกันเท่านั้น
    #     """,
    # ),
    StructuredTool(
        name="Graph",
        func=judgement_cypher_chain.invoke,
        args_schema=GraphToolInput,
        description="""
            ฐานข้อมูล ด้วยการค้นหาด้วยคำสั่ง Cypher ในฐานข้อมูลทั้งหมด เพื่อวิเคราะห์ประเด็นข้อพิพาท, กฎหมายที่ใช้อ้างอิง,
            และผลกระทบของคำพิพากษาต่อคู่กรณี ตอบกลับเป็นภาษาไทยแบบชาวบ้านใช้คุยกันเท่านั้น
        """,
    ),
]

system = '''Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering             simple questions to providing in-depth explanations and discussions on a wide range of             topics. As a language model, Assistant is able to generate human-like text based on             the input it receives, allowing it to engage in natural-sounding conversations and             provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly             evolving. It is able to process and understand large amounts of text, and can use this             knowledge to provide accurate and informative responses to a wide range of questions.             Additionally, Assistant is able to generate its own text based on the input it             receives, allowing it to engage in discussions and provide explanations and             descriptions on a wide range of topics.

Overall, Assistant is a powerful system that can help with a wide range of tasks             and provide valuable insights and information on a wide range of topics. Whether             you need help with a specific question or just want to have a conversation about             a particular topic, Assistant is here to assist.'''

human = '''TOOLS
------
Assistant can ask the user to use tools to look up information that may be helpful in             answering the users original question. The tools the human can use are:

{tools}

RESPONSE FORMAT INSTRUCTIONS
----------------------------

When responding to me, please output a response in one of two formats:

**Option 1:**
Use this if you want the human to use a tool.
Markdown code snippet formatted in the following schema:

```json
{{
    "action": string, \ The action to take. Must be one of {tool_names}
    "action_input": string \ The input to the action
}}
```

**Option #2:**
Use this if you want to respond directly to the human. Markdown code snippet formatted             in the following schema:

```json
{{
    "action": "Final Answer",
    "action_input": string \ You should put what you want to return to use here
}}
```

USER'S INPUT
--------------------
Here is the user's input (remember to respond with a markdown code snippet of a json             blob with a single action, and NOTHING else):

{input}'''

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

agent = create_json_chat_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True, verbose=True)

agent_executor.invoke({"input": "สวัสดี"})

