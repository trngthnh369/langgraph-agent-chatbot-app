# 🤖 Advanced Multi-Agent E-commerce Chatbot

A sophisticated sales chatbot built with **LangGraph**, **Google Gemini AI**, and **ChromaDB** that provides intelligent customer support for e-commerce businesses.

## 🚀 Features

### 🎯 Multi-Agent Architecture
- **Manager Agent**: Routes queries and orchestrates workflow
- **Product Agent**: Handles product-related inquiries with RAG
- **Shop Information Agent**: Manages store information and services
- **Query Rewriter**: Optimizes queries for better results
- **Context Evaluator**: Determines information needs
- **Response Evaluator**: Ensures quality responses

### 🔄 Intelligent Workflow
1. **Query Processing**: Language detection and query optimization
2. **Context Assessment**: Determines if additional information is needed
3. **Source Selection**: Chooses appropriate data sources
4. **Information Retrieval**: RAG from vector database + internet search
5. **Response Generation**: AI-powered responses with context
6. **Quality Assurance**: Automated response evaluation with retry logic

### 🛠 Technical Capabilities
- **Vector Search**: ChromaDB with Gemini embeddings
- **Internet Search**: SerpAPI integration for real-time information
- **Multilingual Support**: Vietnamese and English
- **Retry Logic**: Automatic query rewriting for better results
- **Context-Aware**: Maintains conversation history

## 📋 Prerequisites

- **Python 3.9+**
- **UV package manager** (recommended) or pip
- **Google AI API Key** (Gemini)
- **SerpAPI Key** (optional, for internet search)

## 🛠 Installation

### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/trngthnh369/langgraph-agent-chatbot-sales.git
cd langgraph-agent-chatbot-sales

# Create virtual environment and install dependencies
uv venv
.venv\Scripts\activate
uv pip install -e .
```

### Using Pip

```bash
# Clone the repository
git clone https://github.com/trngthnh369/langgraph-agent-chatbot-sales.git
cd langgraph-agent-chatbot-sales

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Copy environment template**:
```bash
cp .env.example .env
```

2. **Configure your API keys in `.env`**:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here  # Optional
DEBUG=false
LOG_LEVEL=INFO
CHROMA_DB_PATH=./db
```

3. **Get your API keys**:
   - **Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **SerpAPI**: Get from [SerpAPI Dashboard](https://serpapi.com/dashboard) (optional)

## 🗃 Database Setup

### Prepare Your Product Data

1. **Create your product CSV file** (`hoanghamobile.csv`) with columns:
   - `title`: Product name
   - `product_promotion`: Promotional information
   - `product_specs`: Technical specifications
   - `current_price`: Price information
   - `color_options`: Available colors (JSON array format)

### Build Vector Database

```bash
#Using UV
uv run build-vector-search.py
# Using standard Python
python build-vector-search.py
```

This will:
- Process your product data
- Generate embeddings using Gemini API
- Create ChromaDB vector database
- Test the database functionality

## 🚀 Usage

### Start the Chatbot

```bash
# Using UV
uv run app.py

# Using standard Python
python app.py
```

### Deploy with Streamlit

```bash
streamlit run streamlit_app.py
```

### Example Interactions

```
You: Nokia 3210 4G có giá bao nhiêu?
Assistant: Nokia 3210 4G có giá là 1,590,000 ₫. Đây là điện thoại feature phone với kết nối 4G, thiết kế cổ điển và pin lâu dài.

You: Cửa hàng có ở đâu?
Assistant: Chúng tôi có 3 cửa hàng tại Hà Nội:
1. 89 Đ. Tam Trinh, Mai Động, Hoàng Mai - Mở cửa 8:30-21:30
2. 27A Nguyễn Công Trứ, Phạm Đình Hổ, Hai Bà Trưng - Mở cửa 8:30-21:30
3. 392 Đ. Trương Định, Tương Mai, Hoàng Mai - Mở cửa 8:30-21:30

You: What's the best Samsung phone under $300?
Assistant: Based on our current inventory, I'd recommend the Samsung Galaxy A05s...
```

## 🏗 Architecture

### Workflow Diagram

```
Start → Language Detection → Query Rewriting → Agent Routing
                                                     ↓
Context Assessment → Source Selection → Information Retrieval
                                                     ↓
Response Generation → Quality Evaluation → Final Response
                              ↓
                    (If poor quality: retry with rewritten query)
```

### Agent Responsibilities

| Agent | Responsibility | Data Sources |
|-------|---------------|--------------|
| **Manager** | Query routing and orchestration | N/A |
| **Query Rewriter** | Query optimization and refinement | N/A |
| **Context Evaluator** | Determines information requirements | N/A |
| **Source Selector** | Chooses appropriate data sources | N/A |
| **Product Agent** | Product inquiries and recommendations | ChromaDB + Internet |
| **Shop Agent** | Store information and services | Local DB + Internet |
| **Response Evaluator** | Quality assurance and retry logic | N/A |

## 📁 Project Structure

```
langgraph-agent-chatbot-sales/
├── app.py                     # Main application with LangGraph workflow
├── rag.py                     # RAG implementation with Gemini + SerpAPI
├── prompt.py                  # Agent instructions and prompts
├── streamlit_app.py           # Deploy with Streamlit
├── build-vector-search.py     # Vector database builder
├── hoanghamobile.csv          # Product data (you provide this)
├── db/                        # ChromaDB storage (auto-created)
├── pyproject.toml             # UV project configuration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🎛 Configuration Options

### Agent Behavior

Customize agent behavior by modifying `prompt.py`:
- **Response styles**: Formal vs casual
- **Language preferences**: Default language handling
- **Routing logic**: Query classification rules
- **Quality criteria**: Response evaluation standards

### Database Settings

Configure database behavior in `rag.py`:
- **Similarity threshold**: Minimum similarity for relevant results
- **Number of results**: How many documents to retrieve
- **Embedding model**: Gemini embedding model selection
- **Retry logic**: Fallback behavior for failed searches

## 🔧 Troubleshooting

### Common Issues

**1. "No module named 'google.generativeai'"**
```bash
uv pip install google-generativeai
# or
pip install google-generativeai
```

**2. "ChromaDB collection not found"**
```bash
Rebuld the vector database
uv build-vector-search.py
```

**3. "API key not configured"**
- Check your `.env` file
- Ensure `GEMINI_API_KEY` is set correctly
- Verify API key validity at Google AI Studio

**4. "Internet search not working"**
- SerpAPI is optional
- Check `SERPAPI_API_KEY` in `.env`
- The system will work without internet search

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
uv run app.py
```
### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv pip install -e .

CMD ["python", "app.py"]
```

## 🔄 Development

### Adding New Agents

1. **Create agent function** in `app.py`
2. **Add routing logic** in manager agent
3. **Update prompts** in `prompt.py`
4. **Add to StateGraph** workflow
5. **Test thoroughly**

### Extending Data Sources

1. **Add new RAG function** in `rag.py`
2. **Update source selection** logic
3. **Modify agent instructions**
4. **Update error handling**

## 📊 Performance

### Benchmarks

- **Average response time**: 2-5 seconds
- **Query processing**: ~1 second
- **Vector search**: ~200ms
- **Internet search**: 1-3 seconds (when used)
- **Concurrent users**: Scales with API limits

### Optimization Tips

- **Cache frequent queries**
- **Batch process embeddings**
- **Use connection pooling**
- **Implement response caching**
- **Monitor API rate limits**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph** for the multi-agent framework
- **Google Gemini** for advanced AI capabilities
- **ChromaDB** for efficient vector storage
- **SerpAPI** for internet search functionality
- **ProtonX** for the educational foundation

## 🆘 Support

Need help? 

- 📧 **Email**: truongthinhnguyen30303@gmail.com