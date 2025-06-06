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
```

### 2. Create a Python Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install LangChain, LangGraph, and other required libraries.

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open the `.env` file and set your API keys. For example:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Add any other keys needed by your configuration.

### 5. Run the Chatbot

```bash
python main.py
```

This starts the chatbot (e.g. in an interactive CLI or a simple interface). You should see a prompt or greeting message. You can then type questions and the bot will respond.

**Example interaction:**

```
Bot: Hello! How can I assist you today?
You: What is the price of product X?
Bot: [Shows price and details from data]...
```

At this point the chatbot is running locally. It uses the supplied product/store data to answer queries, leveraging LangGraph's multi-agent workflow to determine how to handle each question.

## Data and Extensibility

The project includes sample data files:

- `data/products.json`
- `data/store.json`

To update or expand the bot’s knowledge, you can:

- Edit these data files
- Connect a real database
- Add a new agent (e.g., an order placement agent) by defining a new node in the LangGraph and writing its logic

LangGraph’s framework makes this straightforward.

## Summary

This chatbot demonstrates how LangGraph can manage a multi-agent conversation flow for sales support. By using LangGraph’s structured workflow, it cleanly separates concerns among agents (e.g., product queries vs. store info) while maintaining a coherent dialogue.

The setup above allows anyone to clone the repo, install the requirements, configure API keys, and run the chatbot locally to start interacting with it.

## References

- [A Step-by-Step Guide on how to build a Multi-Agent Chatbot](https://techifysolutions.com/blog/building-a-multi-agent-chatbot-with-langgraph/)
- [LangGraph](https://www.langchain.com/langgraph)
- [GitHub - lucasboscatti/sales-ai-agent-langgraph](https://github.com/lucasboscatti/sales-ai-agent-langgraph)

---

## Contact

For questions or support, please contact: **truongthinhnguyen30303@gmail.com**
