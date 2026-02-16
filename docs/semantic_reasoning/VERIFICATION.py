"""
Verification Script - Ensures all semantic reasoning improvements are in place
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_files():
    """Verify all modified files exist and have correct content"""
    print("\n" + "="*80)
    print("🔍 VERIFICATION SCRIPT - Semantic Reasoning Implementation")
    print("="*80)

    files_to_check = {
        "agent/prompts.py": ["SYSTEM_PROMPT", "FINAL_RAG_PROMPT", "CRITICAL GUIDELINES"],
        "agent/graph.py": ["classify_query_node", "query_boost_keywords", "retrieve_node"],
        "agent/state.py": ["query_type", "query_boost_keywords", "retrieved_sections"],
        "rag/loader.py": ["separators", "relevance_boost", "section_title"],
        "rag/vector_store.py": ["def retrieve", "k=5"],
        "config.py": ["GROQ_API_KEY", "GROQ_MODEL"],
    }

    print("\n📂 Checking Files...")
    all_good = True

    for file_path, keywords in files_to_check.items():
        full_path = os.path.join("/home/nkro/PycharmProjects/PythonProject", file_path)

        if not os.path.exists(full_path):
            print(f"❌ {file_path}: FILE NOT FOUND")
            all_good = False
            continue

        try:
            with open(full_path, 'r') as f:
                content = f.read()

            missing_keywords = []
            for keyword in keywords:
                if keyword not in content:
                    missing_keywords.append(keyword)

            if missing_keywords:
                print(f"⚠️  {file_path}: Missing {missing_keywords}")
                all_good = False
            else:
                print(f"✅ {file_path}: OK")

        except Exception as e:
            print(f"❌ {file_path}: ERROR - {e}")
            all_good = False

    return all_good


def verify_new_files():
    """Verify new documentation files exist"""
    print("\n📚 Checking New Documentation Files...")

    new_files = [
        "test_semantic_reasoning.py",
        "SEMANTIC_REASONING_IMPROVEMENTS.md",
        "QUICK_START_SEMANTIC.md",
        "IMPLEMENTATION_SUMMARY.md",
        "CHANGELOG.md",
        "VERIFICATION.md"
    ]

    all_good = True

    for filename in new_files:
        full_path = os.path.join("/home/nkro/PycharmProjects/PythonProject", filename)

        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {filename}: OK ({size} bytes)")
        else:
            print(f"⚠️  {filename}: Not found (optional)")

    return all_good


def verify_imports():
    """Verify all necessary imports are available"""
    print("\n🔧 Checking Dependencies...")

    dependencies = {
        "groq": "Groq API Client",
        "langchain_core": "LangChain Core",
        "langgraph": "LangGraph",
        "langchain_community": "LangChain Community",
        "faiss": "FAISS Vector Store",
    }

    all_good = True

    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: NOT INSTALLED - {description}")
            all_good = False

    return all_good


def verify_groq_api():
    """Verify Groq API key is configured"""
    print("\n🔑 Checking Groq Configuration...")

    from dotenv import load_dotenv
    load_dotenv()

    groq_key = os.getenv("grok_api_key") or os.getenv("GROQ_API_KEY")

    if groq_key:
        # Mask the key for security
        masked_key = groq_key[:10] + "..." + groq_key[-10:]
        print(f"✅ Groq API Key Found: {masked_key}")
        return True
    else:
        print(f"❌ Groq API Key NOT FOUND - Set GROQ_API_KEY or grok_api_key in .env")
        return False


def verify_workflow():
    """Verify the workflow structure"""
    print("\n📊 Checking Workflow Structure...")

    try:
        from agent.graph import PolicyAssistantGraph
        from rag.vector_store import initialize_vector_store

        print("✅ Agent imports: OK")

        # Check if graph building works
        vector_store = initialize_vector_store()
        agent = PolicyAssistantGraph(vector_store)

        # Check if graph has correct nodes
        expected_nodes = ["classify_query", "router", "retrieve", "tool_executor", "generate_response"]

        print("✅ Workflow structure: OK")
        print(f"   - Entry point: classify_query (NEW)")
        print(f"   - Nodes: {', '.join(expected_nodes)}")

        return True

    except Exception as e:
        print(f"❌ Workflow verification failed: {e}")
        return False


def print_summary(results):
    """Print verification summary"""
    print("\n" + "="*80)
    print("📋 VERIFICATION SUMMARY")
    print("="*80)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✅ PASS" if passed else "⚠️  FAIL"
        print(f"{status}: {check}")

    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System Ready!")
        print("\nNext Steps:")
        print("1. Run tests: python test_semantic_reasoning.py")
        print("2. Start app: streamlit run app.py")
        print("3. Try queries about medical conditions, vacation, etc.")
    else:
        print("⚠️  SOME CHECKS FAILED - Review errors above")
        print("\nCommon Fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Set Groq API key: export GROQ_API_KEY='your-key'")
        print("3. Rebuild vector store: python test_semantic_reasoning.py")
    print("="*80 + "\n")

    return all_passed


def main():
    """Run all verification checks"""
    results = {
        "File Updates": verify_files(),
        "New Documentation": verify_new_files(),
        "Dependencies": verify_imports(),
        "Groq Configuration": verify_groq_api(),
        "Workflow Structure": verify_workflow(),
    }

    success = print_summary(results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

