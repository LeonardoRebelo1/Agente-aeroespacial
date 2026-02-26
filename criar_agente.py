import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.getenv("AZURE_AI_ENDPOINT")
model_name = "gpt-4.1-mini"
agent_name = "Agente-Aeroespacial"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

agent = project_client.agents.get(agent_name)

existing_tools = agent.definition.tools if agent.definition.tools else []

print(f"🔧 Tools encontradas: {len(existing_tools)}")

with open("prompts/system.md", "r", encoding="utf-8") as f:
    instructions_text = f.read()

new_version = project_client.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model=model_name,
        instructions=instructions_text,
        tools=existing_tools,  # 🔥 preserva as tools
    ),
)
