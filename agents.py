
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from tools import web_search, scrape_url

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# LLM
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "YouTube Transcript Chatbot",
    },
    temperature=0
)

# Pull standard ReAct prompt
prompt = hub.pull("hwchase17/react")


# ---------------- SEARCH AGENT ----------------
def build_search_agent():

    agent = create_react_agent(
        llm=llm,
        tools=[web_search],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[web_search],
        verbose=True
    )

    return agent_executor


# ---------------- SCRAPE AGENT ----------------
def build_scrape_agent():

    agent = create_react_agent(
        llm=llm,
        tools=[scrape_url],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[scrape_url],
        verbose=True
    )

    return agent_executor


# ---------------- WRITER CHAIN ----------------
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. Write clear, structured and insightful reports."
    ),
    (
        "human",
        """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all the working URLs found in the research)

Be detailed, factual and professional."""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ---------------- CRITIC CHAIN ----------------
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. Be honest and specific."
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()