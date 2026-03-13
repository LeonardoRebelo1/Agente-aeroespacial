## 🚀 **Agente Aeroespacial Caos**

Agente de **Inteligência Artificial Generativa** especializado em dados aeroespaciais, capaz de consultar APIs da NASA em tempo real, manter memória de conversas e fornecer respostas contextualizadas.

Desenvolvido com arquitetura de microserviços na **Azure**, utilizando Tool Use, Cosmos DB e Azure Functions.

![Agente CAOS](/images/Intro.gif)

---
## 📚 **Introdução**

>**“O mistério gera curiosidade e a curiosidade é a base do desejo humano para compreender.” — Neil Armstrong**

O **Agente Aeroespacial Caos** foi desenvolvido para atuar como um especialista em informações do setor aeroespacial, combinando LLMs com dados reais da **NASA**.

Diferente de chatbots tradicionais, ele utiliza um padrão de Tool Use, permitindo que o modelo:

- identifique quando precisa de dados externos

- execute funções que consultam APIs

- interprete respostas em JSON

- gere respostas amigáveis ao usuário

Além disso, o sistema mantém **memória persistente**, garantindo continuidade nas conversas.

---

## 📝 **Arquitetura do Sistema**

A solução segue uma arquitetura de microserviços distribuídos, hospedada na **Azure**.

![Arquitetura do projeto](/images/Arquitetura.png)

---
## 🧩 **Componentes da Arquitetura**

### 🌐 **Front-End**

##### **Tecnologia**

 - Node.js

##### **Hospedagem**

- Azure App Service (Docker)

##### **Responsabilidades**
- Renderização da interface
- Proxy de API
- Proteção contra acesso direto ao backend
- Controle de CORS

![Front-End do projeto](/images/Front-End.png)

### ⚙️ **Back-End**

##### **Tecnologia**

 - Python 3.11.7 + FastAPI

##### **Hospedagem**

- Azure App Service (Docker)

##### Responsabilidades

- Orquestra requisições

- Gerencia contexto da conversa

- Chama o modelo no Azure AI Foundry

![Front-End do projeto](/images/Back-End.png)

### 🧠 **Inteligência Artificial**

##### **Azure AI Foundry**

- Gerenciar o agente

- Definir comportamento do sistema

- Executar inferência com GPT-4.1-mini

![Azure AI Foundry](/images/Foundry.png)

### 💾 **Persistência de Dados**

##### **Azure Cosmos DB**

 - Histórico de conversas

- Contexto por thread_id

- Memória persistente do agente

![Azure Cosmos DB](/images/CosmosDB.png)

### 🛠 **Ferramentas (Tool Use)**

##### **Azure Functions**

- Executam consultas às APIs da NASA quando o modelo identifica necessidade de dados externos.

![Ferramentas](/images/Funcoes.png)

---
### 🔄 **Fluxo de Execução**

1. Usuário envia pergunta
2. Node.js recebe requisição
3. Requisição é enviada para o backend
4. Backend recupera histórico no Cosmos DB
5. Pergunta +  contexto são enviados ai Azure AI Foundry
6. Se necessário, chama o Azure Function
7. Azure Function consulta API da NASA
8. O agente interpreta o JSON  e gera resposta
9. A resposta é enviada ao usuário

---

### 🛰 **APIs da NASA Utilizadas**

1. **APOD — Astronomy Picture of the Day**

Fornece uma imagem ou vídeo astronômico diário com explicação científica.

O agente pode:

 - Buscar a imagem do dia do nascimento do usuário

 - Explicar o fenômeno astronômico exibido

 ![APOD](/images/APOD.gif)

2. **NeoWs — Near Earth Object Web Service**

Fornece dados sobre asteroides próximos da Terra.

O agente pode:

- Buscar dados sobre asteroides que passaram próximos da Terra e informa a distância o nível de perigo.

![NeoWs](/images/Asteroides.gif)

3. **Earth Observatory Natural Event Tracker (EONET)**

Monitora eventos naturais na Terra, como queimadas, tempestades e erupções vulcânicas, vistos do espaço.

O que o Agente faz: 

- Relaciona a visão espacial com desastres naturais terrestres.

![EONET](/images/EONET.gif)

4. **NASA people in space**

Busca dados em tempo real sobre a presença humana no espaço e busca a localização da estação espacial.

O que o Agente faz: 
- Pode informar quantos astronautas estão atualmente no espaço e quais são seus nomes, além de fornecer a localização atual da Estação Espacial Internacional (ISS) no mapa.

![People in space](/images/pessoas_espaco.gif)

## 🔐 **Segurança e DevOps**

##### 🐳 **Containerização**

Todo o ambiente é padronizado com Docker, garantindo consistência entre desenvolvimento e produção

##### 🔑 **RBAC**

O sistema utiliza **Identidade Gerenciada da Azure** para autenticação segura entre serviços. Isso elimina a necessidade de API keys fixas.

## 🌱 **Variáveis de Ambiente**

| Variável          | Descrição                  |
|-------------------|----------------------------|
| API_BASE_URL      | URL do backend             |
| WEBSITES_PORT     | Portal do container        |
| AZURE_AI_AGENT_ID | ID do agente no AI Foundry |
| COSMOS_ENDPOINT   | Endpoint do Cosmos DB      |

## 👨‍💻 **Autor**

**[Leonardo Bordini Rebelo](https://www.linkedin.com/in/leonardo-bordini-rebelo-5aa5b7281/)**

**📅 Fevereiro de 2026**