## 🤖 MongoDB Data Analyst Agent

This project implements a **LangChain Agent** designed to analyze and visualize data stored in a local MongoDB instance. The agent leverages specialized tools to understand the database schema, perform complex MQL queries, and generate data plots based on natural language commands.

-----

## 🚀 Features

  * **Natural Language Querying:** Convert user questions (e.g., "What is the average math score for females?") into MongoDB queries.
  * **MongoDB Query Tool (`mongo_db_tool`):** Executes complex MongoDB Query Language (MQL) `find()` operations against the database.
  * **Schema Inspection (`get_mongo_document_schema`):** Allows the LLM to inspect the current collection schema for accurate query generation.
  * **Data Visualization (`generate_plot`):** Creates plots (e.g., bar charts, line graphs) in response to visualization requests.

-----

## ⚙️ Setup and Installation

### Prerequisites

  * Python 3.9+
  * A running local **MongoDB Community Edition** instance (default port 27017).
  * Data loaded into your specified collection (e.g., `student_performance`).

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone [YOUR_REPO_URL]
    cd [YOUR_PROJECT_NAME]
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt 
    # (Ensure requirements.txt includes: langchain, pymongo, openai/google-genai, pydantic, matplotlib, etc.)
    ```

3.  **Configure API Key:**
    Set your LLM API key (e.g., OpenAI or Gemini) as an environment variable.

    ```bash
    export OPENAI_API_KEY="your-key-here"
    # OR
    export GEMINI_API_KEY="your-key-here"
    ```
4. ** Run the server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8005 --reload

-----

## 📖 Usage

To interact with the agent, initialize it and invoke it with a user query:

```python
from your_agent_module import agent_chain

# Example user query
user_query = "Plot the distribution of reading scores by parental level of education."

# Invoke the agent
response = agent_chain.invoke({"messages": [{"role": "user", "content": user_query}]})

# Extract the final text response
final_answer = response['messages'][-1].content[0]['text']

print(final_answer)
```

-----

## 🛠️ Tool Definitions

The agent is powered by the following custom tools:

| Tool Name | Purpose | Input Format |
| :--- | :--- | :--- |
| `mongo_db_tool` | Retrieves filtered/aggregated data. | MongoDB MQL Filter (Python `dict`) |
| `get_mongo_document_schema` | Provides collection structure to the LLM. | None |
| `generate_plot` | Creates a visual representation. | Natural language plot description |
