# LangGraph Multi-Agent Sales Chatbot

This project is an AI-powered **multi-agent chatbot** built for e-commerce sales support. It leverages LangChain’s **LangGraph** framework to orchestrate multiple specialized agents, each handling a particular task. For example, one agent might handle product information queries while another handles store details. This multi-agent approach distributes responsibility among agents for better *task specialization* and efficiency. The chatbot uses a dataset of products and store information to answer questions like product availability, pricing, and store hours.

By routing user queries through a LangGraph *StateGraph*, the system maintains conversation context and ensures coherent multi-turn dialogue.

---

## ✨ Features

- **Product Inquiries:** Answers questions about product availability, pricing, and stock levels.
- **Store Information:** Provides store details such as address, hours, and contact info.
- **Stateful Conversation:** Maintains context across multiple user turns for natural interactions.
- **Multi-Agent Workflow:** Uses LangGraph to define and manage specialized agents for different domains (product info, store info, etc.).
- **Extensible Architecture:** Easy to add new agents or data sources.

---

## 🧰 Technologies Used

- **Python 3**
- **[LangChain](https://www.langchain.com/)** & **[LangGraph](https://docs.langchain.com/langgraph/)** for multi-agent orchestration
- **OpenAI or compatible LLM API** for natural language processing
- **dotenv** for environment variable management
- **Simple JSON-based or local data source** for product/store information

---

## ⚙️ Architecture Overview

The chatbot is powered by a **LangGraph StateGraph**:

1. **Chatbot node** receives user input and determines intent.
2. Based on the intent, the message is routed to the appropriate **sub-agent**:
   - *ProductAgent* handles product-related questions.
   - *StoreAgent* handles store-related queries.
3. Each agent uses prompt templates and LLM calls to process requests.
4. LangGraph handles state transitions and memory, ensuring agents can work together across turns.

This **multi-agent setup** allows each part of the system to specialize in a domain while working together seamlessly.

---

## 🛠️ Installation & Local Setup

Follow these steps to run the chatbot locally:

### 1. Clone the Repository

```bash
git clone https://github.com/trngthnh369/langgraph-agent-chatbot-app.git
cd langgraph-agent-chatbot-app
