from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Import your existing RAG tools and prompts
from rag import rag, shop_information_rag, search_internet
from prompt import (
    MANAGER_INSTRUCTION, 
    PRODUCT_INSTRUCTION, 
    SHOP_INFORMATION_INSTRUCTION,
    QUERY_REWRITER_INSTRUCTION,
    CONTEXT_EVALUATOR_INSTRUCTION,
    SOURCE_SELECTOR_INSTRUCTION,
    RESPONSE_EVALUATOR_INSTRUCTION
)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Define our State
class AgentState(TypedDict):
    # The original and processed queries
    original_query: str
    rewritten_query: str
    current_query: str
    language: str
    
    # Loop control
    max_iterations: int
    current_iteration: int
    
    # The conversation history
    messages: List[Dict[str, Any]]
    
    # Agent routing and decisions
    routing_decision: Optional[str]
    needs_additional_info: bool
    selected_sources: List[str]
    
    # RAG and search results
    product_rag_results: Optional[str]
    shop_info_rag_results: Optional[str]
    internet_search_results: Optional[str]
    retrieved_context: Optional[str]
    
    # Response evaluation
    response: Optional[str]
    response_quality_good: bool
    
    # Final response
    final_response: Optional[str]

def detect_language(state: AgentState):
    """Detect the language of the user's query"""
    query = state["original_query"]
    print(f"\n[System] Detecting language for: {query}")

    prompt = f"""
    Detect the language of this query and respond with just the language code:
    Query: {query}
    
    Respond with only: 'vi' for Vietnamese, 'en' for English, or the appropriate language code.
    """
    
    response = model.generate_content(prompt)
    language = response.text.strip().lower()
    
    print(f"[System] Detected language: {language}")
    
    return {
        "language": language,
        "current_query": query,
        "current_iteration": 0,
        "max_iterations": 3
    }

def rewrite_query(state: AgentState):
    """Agent that rewrites the query for better processing"""
    current_query = state["current_query"]
    language = state["language"]
    
    print(f"[System] Rewriting query (Iteration {state['current_iteration'] + 1})")
    
    prompt = f"""
    {QUERY_REWRITER_INSTRUCTION}
    
    Original query: {current_query}
    Language: {language}
    
    Rewrite this query to be more specific and searchable while maintaining the original intent.
    """
    
    response = model.generate_content(prompt)
    rewritten_query = response.text.strip()
    
    print(f"[System] Rewritten query: {rewritten_query}")
    
    return {
        "rewritten_query": rewritten_query,
        "current_query": rewritten_query,
        "current_iteration": state["current_iteration"] + 1
    }

def determine_agent_and_context_need(state: AgentState):
    """Manager agent determines routing and if additional context is needed"""
    query = state["current_query"]
    
    print(f"[System] Determining routing and context needs")
    
    # First determine routing
    routing_prompt = f"""
    {MANAGER_INSTRUCTION}
    
    User query: {query}
    
    Determine if this should be handled by:
    1. "product" - for product related queries
    2. "shop_information" - for store information, hours, location, etc.
    
    Respond with just: "product" or "shop_information"
    """
    
    routing_response = model.generate_content(routing_prompt)
    routing_decision = routing_response.text.strip().lower()
    
    # Then determine if additional context is needed
    context_prompt = f"""
    {CONTEXT_EVALUATOR_INSTRUCTION}
    
    Query: {query}
    Agent type: {routing_decision}
    
    Does this query need additional information beyond basic knowledge?
    Consider if the query is:
    - Very specific about product details
    - About current prices or availability
    - About store locations or hours
    - About recent information
    
    Respond with just: "yes" or "no"
    """
    
    context_response = model.generate_content(context_prompt)
    needs_additional_info = context_response.text.strip().lower() == "yes"
    
    print(f"[System] Routing: {routing_decision}, Needs additional info: {needs_additional_info}")
    
    return {
        "routing_decision": routing_decision,
        "needs_additional_info": needs_additional_info
    }

def select_information_sources(state: AgentState):
    """Agent that selects which sources to use for additional information"""
    query = state["current_query"]
    routing_decision = state["routing_decision"]
    
    print(f"[System] Selecting information sources")
    
    prompt = f"""
    {SOURCE_SELECTOR_INSTRUCTION}
    
    Query: {query}
    Agent type: {routing_decision}
    
    Which information sources should be used? Select from:
    1. "vector_database" - for product information
    2. "shop_database" - for shop information
    3. "internet_search" - for current information or when other sources might not have the answer
    
    You can select multiple sources. Respond with a comma-separated list like: "vector_database,internet_search"
    """
    
    response = model.generate_content(prompt)
    selected_sources = [source.strip() for source in response.text.strip().split(",")]
    
    print(f"[System] Selected sources: {selected_sources}")
    
    return {
        "selected_sources": selected_sources
    }

def retrieve_context(state: AgentState):
    """Retrieve context from selected sources"""
    query = state["current_query"]
    selected_sources = state["selected_sources"]
    
    print(f"[System] Retrieving context from sources: {selected_sources}")
    
    retrieved_context = ""
    
    # Retrieve from vector database (products)
    if "vector_database" in selected_sources:
        try:
            product_rag_results = rag(query)
            retrieved_context += f"Product Information:\n{product_rag_results}\n\n"
            print(f"[System] Retrieved product information")
        except Exception as e:
            print(f"[System] Error retrieving product info: {e}")
    
    # Retrieve from shop database
    if "shop_database" in selected_sources:
        try:
            shop_info_rag_results = shop_information_rag()
            shop_info_text = "\n".join([
                f"Address: {shop['address']}, Hours: {shop['opening_hours']}, Maps: {shop['maps_url']}"
                for shop in shop_info_rag_results
            ])
            retrieved_context += f"Shop Information:\n{shop_info_text}\n\n"
            print(f"[System] Retrieved shop information")
        except Exception as e:
            print(f"[System] Error retrieving shop info: {e}")
    
    # Retrieve from internet search
    if "internet_search" in selected_sources:
        try:
            internet_search_results = search_internet(query)
            retrieved_context += f"Internet Search Results:\n{internet_search_results}\n\n"
            print(f"[System] Retrieved internet search results")
        except Exception as e:
            print(f"[System] Error with internet search: {e}")
    
    return {
        "retrieved_context": retrieved_context
    }

def generate_response(state: AgentState):
    """Generate response based on routing decision and available context"""
    query = state["current_query"]
    routing_decision = state["routing_decision"]
    language = state["language"]
    retrieved_context = state.get("retrieved_context", "")
    
    print(f"[System] Generating response with {routing_decision} agent")
    
    if routing_decision == "product":
        instruction = PRODUCT_INSTRUCTION
    else:
        instruction = SHOP_INFORMATION_INSTRUCTION
    
    prompt = f"""
    {instruction}
    
    User query: {query}
    Language: {language}
    
    {'Retrieved Context: ' + retrieved_context if retrieved_context else 'No additional context available.'}
    
    Provide a helpful and accurate response in {language}.
    """
    
    response = model.generate_content(prompt)
    generated_response = response.text.strip()
    
    print(f"[System] Generated response")
    
    return {
        "response": generated_response
    }

def evaluate_response(state: AgentState):
    """Evaluate if the response adequately answers the query"""
    query = state["current_query"]
    response = state["response"]
    language = state["language"]
    
    print(f"[System] Evaluating response quality")
    
    prompt = f"""
    {RESPONSE_EVALUATOR_INSTRUCTION}
    
    Original query: {query}
    Generated response: {response}
    Language: {language}
    
    Does this response adequately answer the user's question? 
    Consider:
    - Does it directly address what was asked?
    - Is it specific enough?
    - Is it in the correct language?
    - Does it provide useful information?
    
    Respond with just: "yes" or "no"
    """
    
    evaluation_response = model.generate_content(prompt)
    response_quality_good = evaluation_response.text.strip().lower() == "yes"
    
    print(f"[System] Response quality good: {response_quality_good}")
    
    return {
        "response_quality_good": response_quality_good
    }

def finalize_response(state: AgentState):
    """Finalize the response"""
    print(f"[System] Finalizing response")
    
    return {
        "final_response": state["response"]
    }

def handle_no_context_response(state: AgentState):
    """Handle direct response without additional context"""
    query = state["current_query"]
    routing_decision = state["routing_decision"]
    language = state["language"]
    
    print(f"[System] Generating direct response without additional context")
    
    if routing_decision == "product":
        instruction = PRODUCT_INSTRUCTION
    else:
        instruction = SHOP_INFORMATION_INSTRUCTION
    
    prompt = f"""
    {instruction}
    
    User query: {query}
    Language: {language}
    
    Provide a helpful response based on general knowledge. Answer in {language}.
    """
    
    response = model.generate_content(prompt)
    generated_response = response.text.strip()
    
    return {
        "response": generated_response
    }

# Routing functions
def route_context_need(state: AgentState) -> str:
    """Route based on whether additional context is needed"""
    if state["needs_additional_info"]:
        return "select_sources"
    else:
        return "generate_direct"

def route_response_evaluation(state: AgentState) -> str:
    """Route based on response quality and iteration count"""
    if state["response_quality_good"]:
        return "finalize"
    elif state["current_iteration"] >= state["max_iterations"]:
        return "finalize"  # Stop after max iterations
    else:
        return "retry"

def route_agent_type(state: AgentState) -> str:
    """Route to appropriate agent based on routing decision"""
    routing_decision = state.get("routing_decision", "").lower()
    if "product" in routing_decision:
        return "product"
    elif "shop" in routing_decision:
        return "shop_information"
    else:
        return "general"

# Create the StateGraph
agent_graph = StateGraph(AgentState)

# Add nodes
agent_graph.add_node("detect_language", detect_language)
agent_graph.add_node("rewrite_query", rewrite_query)
agent_graph.add_node("determine_agent_and_context_need", determine_agent_and_context_need)
agent_graph.add_node("select_information_sources", select_information_sources)
agent_graph.add_node("retrieve_context", retrieve_context)
agent_graph.add_node("generate_response", generate_response)
agent_graph.add_node("generate_direct_response", handle_no_context_response)
agent_graph.add_node("evaluate_response", evaluate_response)
agent_graph.add_node("finalize_response", finalize_response)

# Define the flow
agent_graph.add_edge(START, "detect_language")
agent_graph.add_edge("detect_language", "rewrite_query")
agent_graph.add_edge("rewrite_query", "determine_agent_and_context_need")

# Add conditional branching for context need
agent_graph.add_conditional_edges(
    "determine_agent_and_context_need",
    route_context_need,
    {
        "select_sources": "select_information_sources",
        "generate_direct": "generate_direct_response"
    }
)

# Continue with context retrieval flow
agent_graph.add_edge("select_information_sources", "retrieve_context")
agent_graph.add_edge("retrieve_context", "generate_response")

# Both paths lead to response evaluation
agent_graph.add_edge("generate_response", "evaluate_response")
agent_graph.add_edge("generate_direct_response", "evaluate_response")

# Add conditional branching for response evaluation
agent_graph.add_conditional_edges(
    "evaluate_response",
    route_response_evaluation,
    {
        "finalize": "finalize_response",
        "retry": "rewrite_query"  # Go back to rewrite query
    }
)

# Final edge
agent_graph.add_edge("finalize_response", END)

# Compile the graph
compiled_graph = agent_graph.compile()

def main():
    
    # Set up conversation history
    conversation_history = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit", "bye", "thoat"]:
            print("Assistant: Goodbye! Have a great day!")
            break
        
        # Prepare the input state for the graph
        input_state = {
            "original_query": user_input,
            "rewritten_query": "",
            "current_query": user_input,
            "language": "en",
            "max_iterations": 3,
            "current_iteration": 0,
            "messages": conversation_history + [{"role": "user", "content": user_input}],
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
        
        try:
            # Invoke the graph with the input state
            result = compiled_graph.invoke(input_state)
            
            # Update conversation history
            final_response = result.get("final_response", "I'm sorry, I couldn't process your request.")
            conversation_history = input_state["messages"] + [{"role": "assistant", "content": final_response}]
            
            # Display the assistant's response
            print(f"\nAssistant: {final_response}")
            
        except Exception as e:
            print(f"\nAssistant: I apologize, but I encountered an error: {str(e)}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    main()