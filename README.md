# LangGraph Multi-Agent Sales Chatbot

This project is an AI-powered **multi-agent chatbot** built for e-commerce sales support. It leverages LangChain’s **LangGraph** framework to orchestrate multiple specialized agents, each handling a particular task. For example, one agent might handle product information queries while another handles store details. This multi-agent approach distributes responsibility among agents for better _task specialization_ and efficiency. The chatbot uses a dataset of products and store information to answer questions like product availability, pricing, and store hours. By routing user queries through a LangGraph _StateGraph_, the system maintains conversation context and ensures coherent multi-turn dialogue.

## Key Features
- **Product Inquiries:** Answers questions about product availability, pricing, and stock levels. For example, it can respond to queries like “What products are in stock?” or “How much does product X cost?”.  
- **Store Information:** Provides details about the store (e.g., location, opening hours, contact info) based on the provided data.  
- **Stateful Conversation:** Keeps track of dialogue context across turns, so the bot can handle follow-up questions naturally. LangGraph inherently maintains state and memory, ensuring agents work coherently.  
- **Multi-Agent Workflow:** Internally uses multiple agents defined in a LangGraph _StateGraph_. A supervising chatbot node routes inputs to the right specialized agent (e.g., product-agent or store-agent) based on the query content. This allows each agent to focus on its domain.  
- **Extensible Architecture:** New agents or tools (such as recommendation or order agents) can be added by defining additional nodes in the LangGraph flow. This modular design scales easily and follows LangGraph’s flexible multi-agent control flow model.

## Technologies Used
- **Python:** The chatbot is implemented in Python 3.  
- **LangChain & LangGraph:** Core frameworks for building the agent workflow. LangGraph provides a sophisticated, stateful agent workflow that simplifies multi-agent orchestration. It allows defining multiple AI agents with specialized responsibilities and routing logic.  
- **LLM (Language Model):** An LLM (such as OpenAI’s GPT-4 or similar) powers the natural language understanding and generation. The agents use prompt templates and chain-of-thought to process user input.  
- **Data Storage:** The project uses a simple data source (e.g., JSON or a lightweight database) containing product and store details. The chatbot queries this data to answer user questions.  
- **dotenv:** For managing environment variables (like API keys) securely.

## Architecture (Multi-Agent Flow)
The chatbot’s logic is defined as a **LangGraph StateGraph**. When a user sends a message, the main chatbot agent (the graph’s entry node) evaluates the intent and routes the query to the appropriate sub-agent. For example, if the user asks about a product, the query goes to the _Product Information Agent_; if the question is about store hours, it goes to the _Store Info Agent_. Each agent processes the input (often calling the LLM with a structured prompt) and updates the conversation state. Because LangGraph maintains state across nodes, the context (previous messages, gathered information) is preserved. This supervisor-worker pattern and stateful design take advantage of multi-agent benefits: specialized expertise per agent and maintainable stateful context.

## Installation and Running Locally

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
