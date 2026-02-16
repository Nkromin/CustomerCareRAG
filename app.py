"""
Streamlit UI for Enterprise Policy Assistant
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from agent.graph import create_agent
from rag.vector_store import initialize_vector_store


# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .tool-call {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_agent():
    """
    Load and cache the agent and vector store
    """
    with st.spinner("🔧 Initializing AI Agent..."):
        # Initialize vector store
        vector_store = initialize_vector_store()

        # Create agent
        agent = create_agent(vector_store)

    st.success("✓ Agent Ready!")
    return agent, vector_store


def initialize_session_state():
    """
    Initialize Streamlit session state
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "tool_calls" not in st.session_state:
        st.session_state.tool_calls = []


def display_chat_history():
    """
    Display conversation history
    """
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message.content)


def display_sidebar(vector_store):
    """
    Display sidebar with information and controls
    """
    with st.sidebar:
        st.markdown("### 🏢 Enterprise Policy Assistant")
        st.markdown("---")

        # Info section
        st.markdown("#### 📋 Capabilities")
        st.markdown("""
        - 📚 Answer policy questions
        - 🎫 Create HR tickets
        - 📊 Check leave balance
        - 💬 Maintain conversation context
        """)

        st.markdown("---")

        # Stats
        st.markdown("#### 📊 Statistics")
        if vector_store.vector_store:
            doc_count = vector_store.vector_store.index.ntotal
            st.info(f"📄 Indexed Documents: {doc_count} chunks")

        st.info(f"💬 Messages: {len(st.session_state.messages)}")

        st.markdown("---")

        # Tool calls
        if st.session_state.tool_calls:
            st.markdown("#### 🔧 Recent Tool Calls")
            for i, tool_call in enumerate(reversed(st.session_state.tool_calls[-5:])):
                with st.expander(f"Call {len(st.session_state.tool_calls) - i}"):
                    st.json(tool_call)

        st.markdown("---")

        # Controls
        st.markdown("#### ⚙️ Controls")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.tool_calls = []
            st.rerun()

        if st.button("🔄 Rebuild Vector Store", use_container_width=True):
            with st.spinner("Rebuilding vector store..."):
                st.cache_resource.clear()
                st.rerun()

        st.markdown("---")

        # Example queries
        st.markdown("#### 💡 Example Queries")
        st.markdown("""
        - "What is the leave policy?"
        - "How many days of remote work?"
        - "Create a ticket for laptop issue"
        - "Check my leave balance"
        - "When are performance reviews?"
        """)

        st.markdown("---")
        st.markdown("#### 🔧 Technical Stack")
        st.markdown(f"""
        - **LLM**: Groq ({config.GROQ_MODEL})
        - **Framework**: LangGraph
        - **Vector Store**: FAISS
        - **Embeddings**: HuggingFace
        """)


def main():
    """
    Main application
    """
    # Initialize
    initialize_session_state()

    # Load agent
    try:
        agent, vector_store = load_agent()
    except Exception as e:
        st.error(f"❌ Failed to load agent: {e}")
        st.stop()

    # Header
    st.markdown('<div class="main-header">🏢 Enterprise Policy Assistant</div>',
                unsafe_allow_html=True)

    # Sidebar
    display_sidebar(vector_store)

    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="info-box">
            <h4>👋 Welcome to the Enterprise Policy Assistant!</h4>
            <p>I can help you with:</p>
            <ul>
                <li>📚 Company policies and procedures</li>
                <li>🎫 Creating HR support tickets</li>
                <li>📊 Checking leave balances</li>
                <li>💬 Answering general questions</li>
            </ul>
            <p><strong>Ask me anything about company policies or HR!</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Display chat history
    display_chat_history()

    # Chat input
    if prompt := st.chat_input("Ask about policies, create tickets, or check leave balance..."):
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Get response from agent
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Invoke agent
                    result = agent.invoke(
                        query=prompt,
                        messages=st.session_state.messages
                    )

                    # Extract response
                    response = result.get("response", "I apologize, I couldn't process that request.")

                    # Display response
                    st.markdown(response)

                    # Update session state
                    st.session_state.messages = result.get("messages", st.session_state.messages)

                    # Store tool calls
                    if result.get("tool_calls"):
                        st.session_state.tool_calls.extend(result["tool_calls"])

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(HumanMessage(content=prompt))
                    st.session_state.messages.append(AIMessage(content=error_msg))


if __name__ == "__main__":
    main()

