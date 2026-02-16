# LangChain + Groq API Sample Application

A comprehensive sample application demonstrating how to use LangChain with the Groq API for fast and efficient language model interactions.

## Features

This application includes 4 practical examples:

1. **Basic Chat** - Simple question-answer interaction with the Groq API
2. **Prompt Templates** - Using structured prompts for better control over queries
3. **Conversation Memory** - Maintaining context across multiple interactions
4. **Batch Processing** - Processing multiple queries efficiently

## Prerequisites

- Python 3.12 or higher
- Groq API key (get one from https://console.groq.com/keys)

## Installation

1. **Clone or set up the project**
   ```bash
   cd /home/nkro/PycharmProjects/PythonProject
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install langchain langchain-groq python-dotenv
   ```

   Or use the project configuration:
   ```bash
   pip install -e .
   ```

## Configuration

1. **Copy the example environment file**
   ```bash
   cp .env.example .env
   ```

2. **Add your Groq API key to `.env`**
   ```
   grok_api_key=your_actual_groq_api_key_here
   ```

## Running the Application

Execute the main script:
```bash
python main.py
```

This will run all four examples and display the results.

## Available Models

The application uses `mixtral-8x7b-32768` by default, but you can also use:
- `llama2-70b-4096`
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`

## Code Examples

### Basic Chat
```python
from langchain_groq import ChatGroq

llm = ChatGroq(api_key="your_key", model="mixtral-8x7b-32768")
response = llm.invoke("What is Python?")
print(response.content)
```

### Using Prompt Templates
```python
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

prompt = ChatPromptTemplate.from_template("Explain {topic} in simple terms")
chain = LLMChain(llm=llm, prompt=prompt)
response = chain.invoke({"topic": "machine learning"})
```

### Conversation with Memory
```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)
response = conversation.predict(input="Hello!")
```

## Troubleshooting

- **"grok_api_key not found in .env file"** - Make sure your `.env` file exists and has the correct API key
- **Connection errors** - Check your internet connection and API key validity at https://console.groq.com/keys
- **Import errors** - Ensure all dependencies are installed: `pip install langchain langchain-groq python-dotenv`

## License

This is a sample application for learning purposes.

