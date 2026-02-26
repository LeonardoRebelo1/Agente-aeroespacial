import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.cosmos import CosmosClient, PartitionKey
import azure.cosmos.exceptions as exceptions
import uvicorn
from typing import Dict, List

load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
AGENT_NAME = "Agente-Aeroespacial"

COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

client_cosmos = CosmosClient(COSMOS_URL, COSMOS_KEY)
database = client_cosmos.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

app = FastAPI(title="API Agente Aeroespacial", version="2.1")

class ChatRequest(BaseModel):
    user_id: str
    thread_id: str
    content: str

def extract_text(response) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text
    try:
        texts = []
        for item in response.output:
            if hasattr(item, "content"):
                for content in item.content:
                    if content.type == "output_text":
                        texts.append(content.text)
        return " ".join(texts)
    except Exception:
        return ""

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        thread_id = request.thread_id 

        try:
            item = container.read_item(item=thread_id, partition_key=thread_id)
            history = item.get("messages", [])
        except exceptions.CosmosResourceNotFoundError:
            history = []

        history.append({"role": "user", "content": request.content})
        
        agent = project_client.agents.get(agent_name=AGENT_NAME)
        response = openai_client.responses.create(
            input=history,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
        )
        assistant_reply = extract_text(response)
        history.append({"role": "assistant", "content": assistant_reply})

        chat_document = {
            "id": thread_id,
            "user_id": request.user_id,
            "messages": history,
            "updated_at": datetime.now().isoformat()
        }
        
        container.upsert_item(chat_document)

        return {
            "response": assistant_reply,
            "thread_id": thread_id,
            "total_messages": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{user_id}")
async def reset_chat(user_id: str):
    try:
        container.delete_item(item=user_id, partition_key=user_id)
        return {"message": f"Histórico do usuário {user_id} limpo com sucesso."}
    except exceptions.CosmosResourceNotFoundError:
        return {"message": "Nenhum histórico encontrado para este usuário."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)