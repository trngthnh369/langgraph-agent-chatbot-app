import streamlit as st
import time
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Import your existing modules
from app import compiled_graph, AgentState
import google.generativeai as genai

load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Sales Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: #e9ecef;
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 2rem;
    }
    
    .system-info {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        font-size: 0.8rem;
        border-left: 4px solid #28a745;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        border-left: 4px solid #dc3545;
    }
    
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .agent-status {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    
    .agent-active {
        background: #fff3cd;
        color: #856404;
        border-left: 4px solid #ffc107;
    }
    
    .agent-completed {
        background: #d1ecf1;
        color: #0c5460;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_queries": 0,
            "successful_responses": 0,
            "product_queries": 0,
            "shop_queries": 0
        }

def display_header():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Sales Assistant</h1>
        <p>Powered by Multi-Agent AI with LangGraph & Gemini</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Status
        st.subheader("🔗 API Status")
        gemini_key = os.getenv("GEMINI_API_KEY")
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        if gemini_key:
            st.success("✅ Gemini API Connected")
        else:
            st.error("❌ Gemini API Not Configured")
        
        if serpapi_key:
            st.success("✅ SerpAPI Connected")
        else:
            st.warning("⚠️ SerpAPI Not Configured (Optional)")
        
        st.divider()
        
        # Chat Settings
        st.subheader("💬 Chat Settings")
        show_system_messages = st.checkbox("Show System Messages", value=False)
        show_agent_workflow = st.checkbox("Show Agent Workflow", value=True)
        max_iterations = st.slider("Max Query Iterations", 1, 5, 3)
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistics")
        stats = st.session_state.stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", stats["total_queries"])
            st.metric("Product Queries", stats["product_queries"])
        
        with col2:
            st.metric("Successful", stats["successful_responses"])
            st.metric("Shop Queries", stats["shop_queries"])
        
        success_rate = (stats["successful_responses"] / stats["total_queries"] * 100) if stats["total_queries"] > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
        
        st.divider()
        
        # Actions
        st.subheader("🔄 Actions")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.success("Chat history cleared!")
            st.rerun()
        
        if st.button("📊 Reset Statistics"):
            st.session_state.stats = {
                "total_queries": 0,
                "successful_responses": 0,
                "product_queries": 0,
                "shop_queries": 0
            }
            st.success("Statistics reset!")
            st.rerun()
        
        # Export chat
        if st.session_state.messages:
            chat_export = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in st.session_state.messages
            ])
            st.download_button(
                "💾 Export Chat",
                chat_export,
                file_name="chat_history.txt",
                mime="text/plain"
            )
    
    return show_system_messages, show_agent_workflow, max_iterations

def display_chat_interface():
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)

def process_query_with_workflow(user_input: str, max_iterations: int, show_system: bool, show_workflow: bool):
    """Process query and show workflow if enabled"""
    
    # Update stats
    st.session_state.stats["total_queries"] += 1
    
    # Create workflow status container
    if show_workflow:
        workflow_container = st.container()
        with workflow_container:
            st.markdown("### 🔄 Agent Workflow")
            workflow_placeholder = st.empty()
    
    # System messages container
    if show_system:
        system_container = st.container()
        with system_container:
            st.markdown("### 🔧 System Messages")
            system_placeholder = st.empty()
    
    # Prepare input state
    input_state = {
        "original_query": user_input,
        "rewritten_query": "",
        "current_query": user_input,
        "language": "en",
        "max_iterations": max_iterations,
        "current_iteration": 0,
        "messages": st.session_state.conversation_history + [{"role": "user", "content": user_input}],
        "routing_decision": None,
        "needs_additional_info": False,
        "selected_sources": [],
        "product_rag_results": None,
        "shop_info_rag_results": None,
        "internet_search_results": None,
        "retrieved_context": None,
        "response": None,
        "response_quality_good": False,
        "final_response": None
    }
    
    workflow_steps = []
    system_messages = []
    
    try:
        # Create a custom callback for workflow tracking
        class WorkflowTracker:
            def __init__(self):
                self.current_step = 0
                self.steps = [
                    "🌐 Detecting Language",
                    "✏️ Rewriting Query", 
                    "🎯 Determining Agent Route",
                    "📊 Evaluating Context Need",
                    "🔍 Selecting Information Sources",
                    "📖 Retrieving Context",
                    "🤖 Generating Response",
                    "✅ Evaluating Response Quality"
                ]
            
            def update_step(self, step_name, status="active"):
                if show_workflow:
                    step_html = ""
                    for i, step in enumerate(self.steps):
                        if step_name in step.lower():
                            step_html += f'<div class="agent-status agent-active">⏳ {step}</div>'
                        elif i < self.current_step:
                            step_html += f'<div class="agent-status agent-completed">✅ {step}</div>'
                        else:
                            step_html += f'<div class="agent-status">⭕ {step}</div>'
                    
                    workflow_placeholder.markdown(step_html, unsafe_allow_html=True)
                    
                if step_name == "completed":
                    self.current_step = len(self.steps)
                else:
                    self.current_step += 1
        
        tracker = WorkflowTracker()
        
        # Process with progress tracking
        with st.spinner("Processing your query..."):
            # Step-by-step processing simulation
            tracker.update_step("detecting")
            time.sleep(0.5)
            
            tracker.update_step("rewriting")
            time.sleep(0.5)
            
            tracker.update_step("determining")
            time.sleep(0.5)
            
            # Execute the actual graph
            result = compiled_graph.invoke(input_state)
            
            tracker.update_step("completed")
        
        # Extract results
        final_response = result.get("final_response", "I'm sorry, I couldn't process your request.")
        routing_decision = result.get("routing_decision", "unknown")
        
        # Update statistics
        st.session_state.stats["successful_responses"] += 1
        if "product" in routing_decision.lower():
            st.session_state.stats["product_queries"] += 1
        elif "shop" in routing_decision.lower():
            st.session_state.stats["shop_queries"] += 1
        
        return final_response, True
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        if show_system:
            system_messages.append(f"❌ {error_msg}")
            system_placeholder.markdown("\n".join([
                f'<div class="error-message">{msg}</div>' 
                for msg in system_messages
            ]), unsafe_allow_html=True)
        
        return f"I apologize, but I encountered an error: {str(e)}\nPlease try again with a different question.", False

def main():
    # Initialize
    initialize_session_state()
    
    # Display components
    display_header()
    show_system, show_workflow, max_iterations = display_sidebar()
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Chat")
        
        # Chat display
        display_chat_interface()
        
        # Input area
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_send = st.columns([4, 1])
            
            with col_input:
                user_input = st.text_input(
                    "Type your message here...",
                    placeholder="Ask about products, prices, store locations, etc.",
                    label_visibility="collapsed"
                )
            
            with col_send:
                submitted = st.form_submit_button("Send 🚀", use_container_width=True)
        
        # Process input
        if submitted and user_input.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Set processing state
            st.session_state.processing = True
            
            # Process query
            response, success = process_query_with_workflow(
                user_input, max_iterations, show_system, show_workflow
            )
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Update conversation history
            st.session_state.conversation_history = [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ]
            
            # Reset processing state
            st.session_state.processing = False
            
            # Rerun to update display
            st.rerun()
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        # Quick query buttons
        quick_queries = [
            "🏪 Cửa hàng ở đâu?",
            "📱 Điện thoại iPhone mới nhất",
            "💰 Samsung Galaxy giá rẻ", 
            "⏰ Giờ mở cửa",
            "🔧 Bảo hành như thế nào?",
            "🚚 Giao hàng mất bao lâu?"
        ]
        
        for query in quick_queries:
            if st.button(query, use_container_width=True):
                # Add to messages and process
                st.session_state.messages.append({"role": "user", "content": query})
                
                response, success = process_query_with_workflow(
                    query, max_iterations, show_system, show_workflow
                )
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.conversation_history.extend([
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response}
                ])
                
                st.rerun()
        
        st.divider()
        
        # Help section
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            **What can I help you with?**
            
            🔍 **Product Information:**
            - Product details and specifications
            - Pricing and availability
            - Product comparisons
            - Recommendations
            
            🏪 **Store Information:**
            - Store locations and directions
            - Opening hours
            - Contact information
            - Services and policies
            
            💡 **Tips:**
            - Be specific in your questions
            - Ask in Vietnamese or English
            - Use the quick action buttons for common queries
            """)
        
        # Language examples
        with st.expander("🌍 Language Examples"):
            st.markdown("""
            **Vietnamese Examples:**
            - "Nokia 3210 4G có giá bao nhiêu?"
            - "Cửa hàng có ở Hai Bà Trưng không?"
            - "Samsung Galaxy A05s có những màu nào?"
            
            **English Examples:**
            - "What's the price of iPhone 15?"
            - "Where is your nearest store?"
            - "What colors does Samsung Galaxy S24 come in?"
            """)

if __name__ == "__main__":
    main()