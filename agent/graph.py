"""
LangGraph Agent Implementation
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json

from agent.state import AgentState
from agent.prompts import (
    SYSTEM_PROMPT, ROUTER_PROMPT, RAG_PROMPT, FINAL_RAG_PROMPT,
    TOOL_SELECTION_PROMPT, FINAL_RESPONSE_PROMPT
)
from agent.tools import TOOL_MAP
from rag.vector_store import VectorStoreManager
import config

# Import Groq
from groq import Groq


class GroqLLM:
    """
    Custom wrapper for Groq LLM compatible with LangChain
    """

    def __init__(self, api_key: str, model: str = config.GROQ_MODEL):
        self.client = Groq(api_key=api_key)
        self.model = model

    def invoke(self, prompt: str, temperature: float = config.TEMPERATURE) -> str:
        """
        Invoke the Groq LLM

        Args:
            prompt: Input prompt
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=1024
            )
            return chat_completion.choices[0].message.content

        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            return f"Error: {str(e)}"


class PolicyAssistantGraph:
    """
    LangGraph-based Policy Assistant Agent
    """

    def __init__(self, vector_store_manager: VectorStoreManager):
        self.llm = GroqLLM(api_key=config.GROQ_API_KEY)
        self.vector_store = vector_store_manager
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        """
        print("🔨 Building LangGraph workflow...")

        # Create graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify_query", self.classify_query_node)
        workflow.add_node("router", self.router_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("tool_executor", self.tool_executor_node)
        workflow.add_node("generate_response", self.generate_response_node)

        # Set entry point
        workflow.set_entry_point("classify_query")

        # Add edge from classify to router
        workflow.add_edge("classify_query", "router")

        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "retrieve": "retrieve",
                "tool": "tool_executor",
                "general": "generate_response"
            }
        )

        # Add edges
        workflow.add_edge("retrieve", "generate_response")
        workflow.add_edge("tool_executor", "generate_response")
        workflow.add_edge("generate_response", END)

        compiled = workflow.compile()
        print("✓ Graph compiled successfully")

        return compiled

    def classify_query_node(self, state: AgentState) -> AgentState:
        """
        Classify query to detect medical, vacation, or other policy categories.
        This helps boost retrieval for semantic reasoning.
        """
        print("\n🏷️  [CLASSIFY QUERY NODE] Analyzing query type...")

        query = state["query"].lower()

        # Define keyword categories for semantic detection
        medical_keywords = [
            'sick', 'ill', 'illness', 'medical', 'health', 'disease', 'condition',
            'fever', 'cold', 'flu', 'infection', 'sinus', 'cough', 'injury', 'pain',
            'surgery', 'hospital', 'doctor', 'treatment', 'medication', 'allergy',
            'allergies', 'migraine', 'headache', 'fatigue', 'body ache', 'unwell',
            'covid', 'diabetes', 'asthma', 'physical', 'mental', 'injury', 'wound'
        ]

        vacation_keywords = [
            'vacation', 'holiday', 'trip', 'travel', 'leisure', 'time off',
            'annual leave', 'break', 'getaway', 'tour'
        ]

        action_keywords = [
            'ticket', 'report', 'complaint', 'issue', 'problem', 'request',
            'help', 'support', 'escalate', 'balance', 'check'
        ]

        query_type = "general"
        query_boost_keywords = ""

        # Classify the query
        if any(keyword in query for keyword in medical_keywords):
            query_type = "medical"
            query_boost_keywords = "sick leave medical condition health illness"
            print(f"   ✓ Detected: MEDICAL/HEALTH CONDITION")
        elif any(keyword in query for keyword in vacation_keywords):
            query_type = "vacation"
            query_boost_keywords = "annual leave vacation time off holiday"
            print(f"   ✓ Detected: VACATION/ANNUAL LEAVE")
        elif any(keyword in query for keyword in action_keywords):
            query_type = "action"
            print(f"   ✓ Detected: ACTION REQUEST")
        else:
            print(f"   ✓ Detected: GENERAL QUERY")

        return {
            **state,
            "query_type": query_type,
            "query_boost_keywords": query_boost_keywords
        }

    def router_node(self, state: AgentState) -> AgentState:
        """
        Route the query to appropriate handler
        """
        print("\n🔀 [ROUTER NODE] Analyzing query...")

        query = state["query"]
        prompt = ROUTER_PROMPT.format(query=query)

        decision = self.llm.invoke(prompt, temperature=0.1).strip().lower()

        # Validate decision
        if "retrieve" in decision:
            decision = "retrieve"
        elif "tool" in decision:
            decision = "tool"
        else:
            decision = "general"

        print(f"   Decision: {decision.upper()}")

        return {
            **state,
            "next_action": decision
        }

    def route_decision(self, state: AgentState) -> Literal["retrieve", "tool", "general"]:
        """
        Conditional edge function
        """
        return state["next_action"]

    def retrieve_node(self, state: AgentState) -> AgentState:
        """
        Retrieve relevant documents from vector store with enhanced semantic search.
        Uses query classification to boost retrieval for policy-related queries.
        """
        print("\n📚 [RETRIEVE NODE] Searching documents with semantic reasoning...")

        query = state["query"]
        query_type = state.get("query_type", "general")
        query_boost_keywords = state.get("query_boost_keywords", "")

        # Build enhanced query
        if query_boost_keywords:
            enhanced_query = f"{query} {query_boost_keywords}"
            print(f"   Query enhancement: {query_type.upper()}")
        else:
            enhanced_query = query

        # Retrieve documents with enhanced query
        # Use k=5 for better coverage with semantic reasoning
        docs = self.vector_store.retrieve(enhanced_query, k=5)

        # Combine context with metadata
        context_parts = []
        section_titles = []

        for doc in docs:
            section = doc.metadata.get('section_title', '')
            content = doc.page_content

            # Format with section header if available
            if section:
                context_parts.append(f"[{section}]\n{content}")
                section_titles.append(section)
            else:
                context_parts.append(content)

        context = "\n\n---\n\n".join(context_parts)

        if context and context != "No relevant information found in policy documents.":
            print(f"   ✓ Found {len(docs)} relevant chunks")
            print(f"   Sections: {', '.join(filter(None, set(section_titles[:3])))}")
        else:
            print("   ⚠️  Limited matches found, using semantic context...")
            # Important: Don't give up. Retrieval returned something, use it for semantic reasoning
            context = "\n\n---\n\n".join(context_parts) if context_parts else "No direct match found, checking policies semantically..."

        return {
            **state,
            "context": context,
            "retrieved_sections": list(set(section_titles))
        }

    def tool_executor_node(self, state: AgentState) -> AgentState:
        """
        Execute appropriate tool
        """
        print("\n🔧 [TOOL EXECUTOR NODE] Selecting and executing tool...")

        query = state["query"]
        prompt = TOOL_SELECTION_PROMPT.format(query=query)

        # Get tool selection from LLM
        response = self.llm.invoke(prompt, temperature=0.1)

        try:
            # Parse JSON response
            tool_info = json.loads(response)
            tool_name = tool_info.get("tool")
            parameters = tool_info.get("parameters", {})

            print(f"   Tool: {tool_name}")
            print(f"   Parameters: {parameters}")

            # Execute tool
            if tool_name in TOOL_MAP:
                tool_func = TOOL_MAP[tool_name]

                # Map parameters to match tool signatures
                mapped_params = parameters.copy()

                # Fix parameter names for create_hr_ticket
                if tool_name == "create_hr_ticket":
                    # Handle various parameter names that LLM might generate
                    issue_text = (
                        mapped_params.get("issue") or
                        mapped_params.get("subject") or
                        mapped_params.get("description") or
                        mapped_params.get("query") or
                        query  # fallback to original query
                    )
                    mapped_params = {"issue": issue_text}

                # Fix parameter names for check_leave_balance
                elif tool_name == "check_leave_balance":
                    employee_id = (
                        mapped_params.get("employee_id") or
                        mapped_params.get("user_id") or
                        "current_user"
                    )
                    mapped_params = {"employee_id": employee_id}

                # Fix parameter names for check_ticket_status
                elif tool_name == "check_ticket_status":
                    ticket_id = mapped_params.get("ticket_id") or mapped_params.get("id")
                    if ticket_id:
                        mapped_params = {"ticket_id": ticket_id}
                    else:
                        mapped_params = {}

                # Invoke tool with mapped parameters
                result = tool_func.invoke(input=mapped_params)

                tool_calls = state.get("tool_calls", [])
                tool_results = state.get("tool_results", [])

                tool_calls.append({"tool": tool_name, "params": mapped_params})
                tool_results.append(result)

                print(f"   ✓ Tool executed successfully")

                return {
                    **state,
                    "tool_calls": tool_calls,
                    "tool_results": tool_results,
                    "context": result
                }
            else:
                print(f"   ⚠️  Unknown tool: {tool_name}")
                return {
                    **state,
                    "context": "Tool not found"
                }

        except json.JSONDecodeError:
            print(f"   ⚠️  Could not parse tool selection")
            # Fallback: try to match tool names in response
            if "create_hr_ticket" in response.lower():
                result = TOOL_MAP["create_hr_ticket"].invoke(input={"issue": query})
                return {
                    **state,
                    "tool_calls": [{"tool": "create_hr_ticket", "params": {"issue": query}}],
                    "tool_results": [result],
                    "context": result
                }
            elif "check_leave_balance" in response.lower():
                result = TOOL_MAP["check_leave_balance"].invoke(input={"employee_id": "current_user"})
                return {
                    **state,
                    "tool_calls": [{"tool": "check_leave_balance", "params": {"employee_id": "current_user"}}],
                    "tool_results": [result],
                    "context": result
                }
            elif "check_ticket_status" in response.lower():
                result = TOOL_MAP["check_ticket_status"].invoke(input={})
                return {
                    **state,
                    "tool_calls": [{"tool": "check_ticket_status", "params": {}}],
                    "tool_results": [result],
                    "context": result
                }
            else:
                return {
                    **state,
                    "context": "Could not determine appropriate tool"
                }

    def generate_response_node(self, state: AgentState) -> AgentState:
        """
        Generate final response with semantic reasoning
        """
        print("\n💬 [GENERATE RESPONSE NODE] Creating response...")

        query = state["query"]
        context = state.get("context", "")
        tool_results = state.get("tool_results", [])
        next_action = state.get("next_action", "general")
        retrieved_sections = state.get("retrieved_sections", [])

        # Generate appropriate response based on action
        if next_action == "retrieve":
            # For policy questions, use semantic reasoning
            # Pass context even if limited, let LLM do semantic analysis
            if context and context != "No relevant information found in policy documents.":
                prompt = FINAL_RAG_PROMPT.format(
                    query=query,
                    context=context,
                    sections=", ".join(retrieved_sections) if retrieved_sections else "various"
                )
            else:
                # Even with limited context, try semantic reasoning
                prompt = FINAL_RAG_PROMPT.format(
                    query=query,
                    context=context if context else "No specific policy matches found",
                    sections="policy documents"
                )
            response = self.llm.invoke(prompt, temperature=0.2)  # Slightly higher temp for reasoning
        elif next_action == "tool" and tool_results:
            # Tool results are already formatted, use them directly
            response = tool_results[0] if tool_results else "Tool execution completed."
        else:
            # General response
            response = self.llm.invoke(query, temperature=0.1)

        print(f"   ✓ Response generated")

        # Update messages
        messages = list(state.get("messages", []))
        messages.append(HumanMessage(content=query))
        messages.append(AIMessage(content=response))

        return {
            **state,
            "response": response,
            "messages": messages
        }

    def invoke(self, query: str, messages: list = None) -> dict:
        """
        Run the agent graph

        Args:
            query: User query
            messages: Conversation history

        Returns:
            Final state with response
        """
        query_str = str(query) if not isinstance(query, str) else query
        print(f"\n{'='*60}")
        print(f"🤖 AGENT INVOKED: {query_str[:50]}...")
        print(f"{'='*60}")

        # Initialize state
        initial_state = {
            "query": query,
            "messages": messages or [],
            "query_type": "general",
            "query_boost_keywords": "",
            "context": "",
            "retrieved_sections": [],
            "next_action": "",
            "tool_calls": [],
            "tool_results": [],
            "response": "",
            "iteration": 0
        }

        # Run graph
        try:
            final_state = self.graph.invoke(initial_state)

            print(f"\n{'='*60}")
            print(f"✓ AGENT COMPLETED")
            print(f"{'='*60}\n")

            return final_state

        except Exception as e:
            print(f"\n❌ Agent Error: {e}")
            return {
                **initial_state,
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "messages": initial_state["messages"] + [
                    HumanMessage(content=query),
                    AIMessage(content=f"Error: {str(e)}")
                ]
            }


def create_agent(vector_store_manager: VectorStoreManager) -> PolicyAssistantGraph:
    """
    Factory function to create the agent

    Args:
        vector_store_manager: Initialized vector store

    Returns:
        PolicyAssistantGraph instance
    """
    return PolicyAssistantGraph(vector_store_manager)

