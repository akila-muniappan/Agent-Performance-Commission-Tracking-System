from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.tools import tool
#from langchain.agents import AgentExecutor
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
import os
import httpx
from langchain_core.messages import AIMessage

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
import urllib3
import numpy as np
import ssl
import json

# --- Setup cache directory ---
tiktoken_cache_dir = "./tiktoken_cache"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

# --- Disable SSL verification (temporary) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
client = httpx.Client(verify=False, timeout=None)

# Initialize the LLM

llm = ChatOpenAI(
    base_url="https://genailab.tcs.in",
    model="azure/genailab-maas-gpt-4o-mini",
    api_key="sk-Eyn8LNkX3vfKQf5CNAkFcw",
    http_client=client
)

#create agents
agent = create_agent(
    model=llm,
)

premimum_system_prompt = """ 
    You are an expert Insurance Agent assistant. The user will provide a insurance agent id. 
    Your input is a JSON format that contains multiple client details. 
    You inputs are 
        a. Policy Type 
        b. premiumAmount
        c. policySoldDate 
        d. policyExpiryDate
        e. targetAmount
        f. regionName
    You need to provide the folloing output by Considering Today's date as 21-Nov-2025
        a. Total premiumAmount - Calculate the total premiumamount for each policy type. 
        b. Average Tenure - calculate tenure of each policy (in months) based on policySoldDate & policyExpiryDate. Then take the average of all tenures. 
        c. Agent Commission - agent commission is 10% of the Total premiumAmount calculated. 
        d. Count of Premiums - Calculate the Total number of Premiums sold in last 6 months based on the policySoldDate. 
        e. Agent Productivity - This is a percentage. Calculte the total premiumamount for all policies sold in the last 6 months and return the percentage of that total value against the targetAmount.
        f. Average Policy Value - Find the average  of premiumAmount of all policies sold in the last 3 months. 
    provide the above 4 values as a JSON. 
"""

# Load JSON having agent data.
filename='new_agent20.json'
with open(filename, 'r') as file:
    data = json.load(file)
    
def calculate_premium_for_agent(agent_id: str) -> str:
    """Calculates the total premium for the agent"""
    if agent_id not in data:
        return f"Error: Agent ID '{agent_id}' not found in the data."
    
    clients = str(data[agent_id]['salesDetails'])
    
    result = agent.invoke(
    {"messages": [
    {"role": "system", "content": premimum_system_prompt},
    {"role": "user", "content": clients}
    ]},
    context={"user_role": "expert"}
    )

    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.content:
            print(msg.content)
            output = msg.content
    return output

# @tool
# def get_bird_details(query: str) -> str:
#     """Returns details about bird species from the text."""
#     results = db.similarity_search(query, k=3)
#     final_string = [r.page_content for r in results]
#     return final_string


def main():
    # Get agent ID from user input
    #agent_id = input("Enter the agent ID (e.g., AGT-10234): ")
    agent_id = 'AGT-10238'
    # Call the calculate_premium_for_agent method
    result = calculate_premium_for_agent(agent_id)
    
    # Print the result
    print("\n" + result)


if __name__ == "__main__":
    main()
