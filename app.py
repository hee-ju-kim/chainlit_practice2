from db.mongo import init_db
from services.user import login
from config.config import settings

from operator import itemgetter

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough, RunnableLambda
from langchain.memory import ConversationBufferMemory
from typing import cast
from chainlit.data.base import BaseDataLayer

import chainlit as cl
from chainlit.types import ThreadDict

from mongo_data_layer import MongoDataLayer
from chainlit.data.storage_clients.s3 import S3StorageClient

storage_client = S3StorageClient(bucket=settings.S3_BUCKET)

@cl.data_layer
def get_data_layer():
  return MongoDataLayer()

# DB 연결
init_db()

def setup_runnable():
  memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

  print(memory)
  model = ChatOpenAI(streaming=True)
  prompt = ChatPromptTemplate.from_messages(
      [
          ("system", "너는 여행 전문가야. 세계에서 안가본곳이 없지. 사람들한테 잘 안알려진 여행지까지 다 알고있어."),
          MessagesPlaceholder(variable_name="history"),
          ("human", "{question}"),
      ]
  )

  runnable = (
      RunnablePassthrough.assign(
          history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
      )
      | prompt
      | model
      | StrOutputParser()
  )
  cl.user_session.set("runnable", runnable)

@cl.on_chat_start
async def on_chat_start():
  # model = ChatOpenAI(streaming=True)
  # prompt = ChatPromptTemplate.from_messages(
  #   [
  #     (
  #       "system",
  #       "너는 여행 전문가야. 세계에서 안가본곳이 없지. 사람들한테 잘 안알려진 여행지까지 다 알고있어.",
  #     ),
  #     ("human", "{question}"),
  #   ]
  # )
  # runnable = prompt | model | StrOutputParser()
  # cl.user_session.set("runnable", runnable)

  image = cl.Image(path="./public/img/루피8.jpg", name="cat image", display="page")
  app_user = cl.user_session.get("user")
  await cl.Message(f"어서오세용 {app_user.metadata["name"]}님\n가고싶은 여행지가 있으신가용?",  elements=[image],).send()

  cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
  setup_runnable()

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
  print('on_chat_resume')
  memory = ConversationBufferMemory(return_messages=True)
  root_messages = [m for m in thread["steps"] if m["parentId"] == None]
  for message in root_messages:
      if message["type"] == "user_message":
          memory.chat_memory.add_user_message(message["output"])
      else:
          memory.chat_memory.add_ai_message(message["output"])

  cl.user_session.set("memory", memory)

  setup_runnable()

@cl.on_message
async def on_message(message: cl.Message):
  memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

  runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

  msg = cl.Message(content="")

  async for chunk in runnable.astream(
    {"question": message.content},
    config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
  ):
    await msg.stream_token(chunk)

  await msg.send()
  memory.chat_memory.add_user_message(message.content)
  memory.chat_memory.add_ai_message(msg.content)

  print('메시지', memory)

@cl.password_auth_callback
def auth_callback(username: str, password: str):
  user = login(username, password)
  if user:
    return cl.User(
      identifier=user["id"], metadata={"name": user["name"]}
    )
  else:
    return None