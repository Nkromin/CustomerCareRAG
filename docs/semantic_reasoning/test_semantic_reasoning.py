"""
Test script to demonstrate improved semantic reasoning for indirect policy questions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from agent.graph import create_agent
from rag.vector_store import initialize_vector_store


def test_semantic_reasoning():
    """Test the improved semantic reasoning with sample queries"""

    print("\n" + "="*80)
    print("🧪 SEMANTIC REASONING TEST - Enterprise Policy Assistant")
    print("="*80)

    # Initialize vector store
    print("\n📦 Initializing vector store...")
    vector_store = initialize_vector_store()

    # Create agent
    print("\n🤖 Creating agent...")
    agent = create_agent(vector_store)

    # Test cases for semantic reasoning
    test_cases = [
        {
            "query": "Can I take leave for sinus infection?",
            "expected": "Should recognize sinus as medical condition → Sick Leave policy"
        },
        {
            "query": "I have a fever, can I stay home?",
            "expected": "Should recognize fever as illness → Sick Leave policy"
        },
        {
            "query": "What if I need surgery?",
            "expected": "Should recognize surgery as medical condition → Sick Leave policy"
        },
        {
            "query": "Can I take time off for my vacation?",
            "expected": "Should recognize vacation → Annual Leave policy"
        },
        {
            "query": "I'm not feeling well due to an infection",
            "expected": "Should recognize infection as health issue → Sick Leave policy"
        },
        {
            "query": "What's the leave balance for me?",
            "expected": "Should use check_leave_balance tool"
        }
    ]

    print("\n" + "="*80)
    print("🧪 Running Test Cases")
    print("="*80)

    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {idx}: {test['query']}")
        print(f"Expected: {test['expected']}")
        print(f"{'─'*80}")

        try:
            # Run the agent
            result = agent.invoke(test['query'])

            response = result.get('response', 'No response')

            print(f"\n✓ RESPONSE:")
            print(f"{response}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("✓ Test Suite Completed")
    print("="*80)


if __name__ == "__main__":
    test_semantic_reasoning()

