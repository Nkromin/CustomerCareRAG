# Quick Start Guide - Semantic Reasoning Improvements

## 🚀 What Changed?

Your LangGraph + Groq RAG agent now has **intelligent semantic reasoning** to handle indirect policy questions.

### Example: The Problem We Fixed

**Before:**
```
User: "Can I take leave for sinus?"
Agent: "I don't have that information in policy documents."
```

**After:**
```
User: "Can I take leave for sinus?"
Agent: "Sinus infection qualifies as a medical condition. Under the Sick Leave Policy, 
        employees are entitled to 12 days of paid sick leave annually. 
        A medical certificate is required if leave exceeds 3 consecutive days."
```

## 🎯 How It Works

### 1. Query Classification
The agent first detects the **type** of your question:
- 🏥 **Medical**: sinus, fever, cold, surgery, infection → Sick Leave
- 🏖️ **Vacation**: vacation, holiday, trip, time off → Annual Leave  
- 🎯 **Action**: create ticket, check balance → Use tools
- ❓ **General**: other questions

### 2. Smart Retrieval
Based on the type, the agent **boosts** the search:
- Medical queries: Adds "sick leave medical condition illness" to search
- Vacation queries: Adds "annual leave vacation time off" to search
- Retrieves **5 policy chunks** (not 4) for better coverage

### 3. Semantic Reasoning
The LLM applies **category logic**:
- "Sinus infection" = specific condition
- "Sinus" matches "medical conditions" category
- Category applies to "Sick Leave" policy
- Answer is YES with policy details

### 4. Reference Tracking
The agent:
- Shows which policy section applied
- Explains WHY (the logical connection)
- Provides relevant details
- Never just says "I don't know"

## 📁 Files Changed

```
✓ agent/prompts.py          - Better prompts with semantic reasoning
✓ agent/graph.py             - New classify_query_node, enhanced retrieval
✓ agent/state.py             - New state fields for classification
✓ rag/loader.py              - Better document splitting, enhanced examples
✓ rag/vector_store.py        - Support for dynamic k parameter
✓ test_semantic_reasoning.py - Test script (NEW)
✓ SEMANTIC_REASONING_IMPROVEMENTS.md - Full documentation (NEW)
```

## 🧪 Test It

Run the test suite:
```bash
python test_semantic_reasoning.py
```

Or use Streamlit:
```bash
streamlit run app.py
```

## 🔍 Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Query Type Detection | ❌ None | ✅ Classified (medical, vacation, action, general) |
| Query Expansion | ❌ Basic | ✅ Smart boost based on type |
| Retrieval Coverage | ❌ k=4 | ✅ k=5 for better context |
| Semantic Reasoning | ❌ Keyword matching | ✅ Category inference |
| False Refusals | ❌ Common | ✅ Rare (uses relevance check) |
| Explanation Quality | ❌ Generic | ✅ Shows policy section & reasoning |

## 💡 Key Prompts

### System Prompt
Now has **CRITICAL GUIDELINES** for semantic reasoning:
- Use category logic, not just keywords
- Medical conditions → Sick Leave
- Vacation → Annual Leave

### Final RAG Prompt
Teaches LLM to:
- Recognize specific situations (sinus) vs. general categories (medical)
- Apply semantic logic ("sinus" matches "medical conditions" category)
- Reference policy sections explicitly
- Explain the logical connection

## 🏗️ Workflow Architecture

```
User Input
    ↓
classify_query (NEW!)
    ↓
router
    ↓
┌─────────────────────┐
│ retrieve | tool     │
│ general             │
└─────────────────────┘
    ↓
generate_response (improved!)
    ↓
Output
```

## ⚙️ Configuration

No changes needed! Works with existing config:
- `GROQ_MODEL = "llama-3.1-8b-instant"`
- `CHUNK_SIZE = 800`
- `CHUNK_OVERLAP = 150`
- `TEMPERATURE = 0.1`

## 🎓 Learning Examples

### Example 1: Sinus Question
```
Input: "Can I take leave for sinus infection?"

Step 1 - Classify: Medical query detected
Step 2 - Boost: Query becomes "...sick leave medical condition illness"
Step 3 - Retrieve: Gets Sick Leave policy section
Step 4 - Reason: "Sinus" matches "medical conditions" in policy
Step 5 - Answer: "Yes, under Sick Leave Policy, employees get 12 days..."
```

### Example 2: Vacation Question
```
Input: "What if I want to go on a vacation?"

Step 1 - Classify: Vacation query detected
Step 2 - Boost: Query becomes "...annual leave vacation time off"
Step 3 - Retrieve: Gets Annual Leave policy section
Step 4 - Reason: "Vacation" matches "annual leave" policy
Step 5 - Answer: "Yes, under Annual Leave Policy, employees get 20 days..."
```

### Example 3: Cold/Fever
```
Input: "I'm sick with a bad cold"

Step 1 - Classify: Medical query detected
Step 2 - Boost: Query becomes "...sick leave medical condition illness"
Step 3 - Retrieve: Gets Sick Leave section (mentions "cold, flu, infectious")
Step 4 - Reason: "Cold" explicitly mentioned in policy examples
Step 5 - Answer: "Cold is covered under Sick Leave. You can take up to 12 days..."
```

## 🔧 Troubleshooting

### Q: Agent still says "I don't know" for indirect questions?
**A:** 
- Make sure vector store is rebuilt: `python test_semantic_reasoning.py`
- Check that sample document has detailed Sick Leave section
- Verify retrieval is returning policy chunks

### Q: Responses are too generic?
**A:** 
- Increase context window in FINAL_RAG_PROMPT
- Ensure policy documents have specific examples
- Check that section headers are preserved in chunks

### Q: Too slow?
**A:**
- Classification is just keyword matching (~1ms)
- Retrieval is same as before (just slightly more chunks)
- No additional LLM calls
- Overall impact: negligible

## 📚 Related Documentation

See detailed technical docs in:
- `SEMANTIC_REASONING_IMPROVEMENTS.md` - Full architectural details
- `README.md` - Project overview
- `OPTIMIZATIONS.md` - Performance tips

## 🎯 What's Next?

Recommended enhancements:
1. Add confidence scoring ("I'm 90% sure...")
2. Show which section was used ("From Sick Leave Policy")
3. Multi-turn context ("Based on our earlier discussion...")
4. User feedback loop ("Was this helpful?")

## ✅ Verification Checklist

- [ ] Vector store initialized with new document format
- [ ] `test_semantic_reasoning.py` runs without errors
- [ ] Streamlit app loads without issues
- [ ] Agent responds to indirect medical questions
- [ ] Agent responds to indirect vacation questions
- [ ] Responses reference policy section names
- [ ] No OpenAI dependencies (Groq only)

## 🤝 Support

If you encounter issues:
1. Check `test_semantic_reasoning.py` output
2. Review `SEMANTIC_REASONING_IMPROVEMENTS.md` for technical details
3. Verify all files have been updated correctly
4. Check Groq API key in `.env` file

---

**Last Updated:** February 16, 2026
**Version:** 2.0 - Semantic Reasoning Edition

