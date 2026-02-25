from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import uvicorn
from typing import Dict, List

PROJECT_ENDPOINT = "https://afAgentes.services.ai.azure.com/api/projects/proj-aeroespacial"
AGENT_NAME = "Agente-Aeroespacial"

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

app = FastAPI(title="API Agente Aeroespacial", version="2.1")

# =========================
# ARMAZENAMENTO DE CONTEXTO
# (Trocar por banco em produção)
# =========================

conversations: Dict[str, List[dict]] = {}

class ChatRequest(BaseModel):
    user_id: str
    content: str

def extract_text(response) -> str:
    """
    Extrai texto da resposta da Azure OpenAI
    Trata casos onde output_text vem vazio
    """
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
        agent = project_client.agents.get(agent_name=AGENT_NAME)

        if request.user_id not in conversations:
            conversations[request.user_id] = []

        history = conversations[request.user_id]

        history.append({
            "role": "user",
            "content": request.content
        })

        response = openai_client.responses.create(
            input=history,
            extra_body={
                "agent": {
                    "name": agent.name,
                    "type": "agent_reference"
                }
            }
        )
        print(response.model_dump())
        assistant_reply = extract_text(response)

        history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        conversations[request.user_id] = history

        return {
            "response": assistant_reply,
            "total_messages": len(history)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{user_id}")
async def reset_chat(user_id: str):
    if user_id in conversations:
        del conversations[user_id]
    return {"message": "Conversa resetada com sucesso"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    