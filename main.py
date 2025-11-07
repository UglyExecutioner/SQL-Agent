import json
import traceback
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib
import re
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#langchain imports
from langchain_core.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

# Starlette imports
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from starlette.requests import Request

# Functional imports
from db.mongo_db import find_documents
load_dotenv('.env')

# Create the langchain tool
class MongoDBTool(BaseTool):
    name: str = "mongo_db_tool"
    description: str = "A tool for interacting with MongoDB databases."

    def _run(self, query: str) -> str:
        # Implement MongoDB interaction logic here
        return find_documents(query=query)

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async not implemented for MongoDBTool")
    
mongo_tool = MongoDBTool()

@tool
def get_mongo_document_schema() -> str:
    """
    Returns the schema of the MongoDB documents.
    """
    schema = {
        "collection_name": os.getenv("MONGO_COLLECTION_NAME"),
        "fields": {
            "_id": "ObjectId",
            "gender": "string",
            "race/ethnicity": "string",
            "parental level of education": "string",
            "lunch": "string",
            "test preparation course": "string",
            "math score": "integer",
            "reading score": "integer",
            "writing score": "integer"
        }
    }
    return json.dumps(schema, indent=2)

schema_tool = get_mongo_document_schema

@tool
def generate_plot(data_json: str, plot_instructions: str) -> str:
    """
    Generates a plot based on the provided data and instructions.
    """
    try:
        data = pd.read_json(data_json)
        plt.figure()

        if "line plot" in plot_instructions.lower():
            for column in data.select_dtypes(include=['number']).columns:
                plt.plot(data.index, data[column], label=column)
            plt.title("Line Plot")
            plt.xlabel("Index")
            plt.ylabel("Values")
            plt.legend()
        elif "bar chart" in plot_instructions.lower():
            data.plot(kind='bar')
            plt.title("Bar Chart")
            plt.xlabel("Index")
            plt.ylabel("Values")
        else:
            return "Unsupported plot type."

        plot_filename = "generated_plot.png"
        plt.savefig(plot_filename)
        plt.close()
        return f"Plot saved as {plot_filename}"
    except Exception as e:
        return f"Error generating plot: {str(e)}"

plot_tool = generate_plot

def gemini_llm(user_query: str):
    try:
        system_prompt = """
            ## 🤖 Data Analyst Agent System Prompt (Revised for MongoDB MQL)

            ### 🎯 Primary Goal
            You are an expert data analyst and visualization specialist for a MongoDB database. Your goal is to answer user questions about the data by strictly leveraging the provided tools. If a question is about data retrieval or computation, use the MongoDB tools. If it's about visual representation, use the plotting tool.

            ---

            ### 🛠️ Available Tools and Usage Guidelines

            You have access to the following three specialized tools. Your decision process must follow this flow:

            1. **`get_mongo_document_schema`**:
                * **Intent:** Use this **first** if the user asks for information about the **database structure, fields, columns, or schema**.
                * **Priority:** Use this immediately if schema information is explicitly requested or if you need to inspect the schema to formulate an accurate query for the `mongo_db_tool`.
                * **Output:** Returns a JSON representation of the collection schema.

            2. **`mongo_db_tool`**:
                * **Intent:** Use this for any question requiring **data retrieval, aggregation, filtering, or computation** from the database.
                * **Input:** The input to this tool **must be a syntactically correct MongoDB Query Language (MQL) dictionary**, exactly as it would appear inside a Python `db.collection.find()` call.
                * **Example MQL Input:** `{"gender": "female", "math score": {"$gt": 80}}`
                * **Constraint:** If the user asks for a plot, **do not** use this tool first; use `generate_plot` instead.

            3. **`generate_plot`**:
                * **Intent:** Use this if the user explicitly asks to **"plot," "visualize," "show a chart," or "graph"** the data.
                * **Input:** The input to this tool must be a clear, natural language description of **what to plot**, including the variables and the desired plot type (e.g., "bar chart of average math scores by gender").
                * **Output:** Returns a markdown image tag or file path for the generated plot.

            ---

            ### 📝 Constraint and Formatting Rules
            * **Self-Correction:** If a tool fails or returns inadequate information, try to adjust your approach or use a different tool. For example, if `mongo_db_tool` fails, use `get_mongo_document_schema` to verify the field names and try again.
            * **Final Answer:** Only provide a final answer when the tool output is sufficient and directly addresses the user's question.
            * **Do not hallucinate data.** All data-related answers must come from the tools.
            * **Prioritize tool use.** If a tool can answer the question, you must use it.
        """
            
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        agent = create_agent(
            llm,
            tools=[mongo_tool, schema_tool, plot_tool],
            system_prompt=system_prompt
        )
        response = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
        # print(response)
        return response['messages'][-1].content[0]['text']
    except Exception as e:
        traceback.print_exc()
        return f"Error: {str(e)}"
    
async def rag_chat(request: Request):
    try:
        data = await request.json()
        user_query = data.get("message", "")
        response = gemini_llm(user_query)
        return JSONResponse({"response": response})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
    
# Starlette app setup
templates = Jinja2Templates(directory="templates")

async def homepage(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

routes = [
    Route("/", homepage, name="homepage"),
    Route("/rag_chat", rag_chat, name="rag_chat", methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)