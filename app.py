import chainlit as cl
from db.mongo import init_db
from services.user import login

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableConfig
from typing import cast

# 앱 시작 시 MongoDB 연결 및 기본 계정 생성
init_db()

@cl.on_chat_start
async def on_chat_start():
  print('on_chat_start')

  model = ChatOpenAI(model="gpt-4o-mini", streaming=True)
  prompt = ChatPromptTemplate.from_messages(
      [
          (
              "system",
              "너는 세계여행 전문가야. 잘 알려지지 않은곳까지 세계일주를 완료하고 온 여행가지.",
          ),
          ("human", "{question}"),
      ]
  )
  runnable = prompt | model | StrOutputParser()
  cl.user_session.set("runnable", runnable)

  app_user = cl.user_session.get("user")
  await cl.Message(f"어서오세용 {app_user.metadata["name"]}님\n가고싶은 여행지가 있으신가용?").send()


@cl.on_message
async def on_message(message: cl.Message):
  runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

  msg = cl.Message(content="")

  async for chunk in runnable.astream(
      {"question": message.content},
      config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
  ):
      await msg.stream_token(chunk)

  await msg.send()

@cl.password_auth_callback
def auth_callback(username: str, password: str):
  user = login(username, password)
  if user:
    return cl.User(
      identifier=user["id"], metadata={"name": user["name"]}
    )
  else:
    return None