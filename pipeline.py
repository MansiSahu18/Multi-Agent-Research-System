import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain
from dotenv import load_dotenv

load_dotenv()

# --- Initialize OpenRouter Embeddings ---
# We point the standard OpenAI class to OpenRouter's endpoint
embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small", # Or any model OpenRouter supports
    openai_api_key=os.getenv("OPENROUTER_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    headers={
        "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
        "X-Title": "ResearchMind"               # Optional identification
    }
)

vectorstore = Chroma(
    collection_name="research_memory",
    embedding_function=embeddings,
    persist_directory="./chroma_db" 
)

def get_or_gather_data(topic: str) -> dict:
    """Checks memory for the topic. If not found, gathers new data."""
    print("\n" + "="*50)
    print(f"Checking memory for: {topic}")
    print("="*50)

    # 1. Search ChromaDB using metadata filtering for an exact topic match
    # We use similarity search, but strictly filter for the exact topic string.
    past_research = vectorstore.similarity_search(
        query=topic, 
        k=1, 
        filter={"topic": topic}
    )

    if past_research:
        print("🧠 Memory Hit! Found existing research. Skipping web scrape.")
        return {
            "search_results": "Retrieved from ChromaDB memory.",
            "scraped_content": past_research[0].page_content
        }

    # 2. If no memory is found, run the agents
    print("🌐 No memory found. Running live web search and scrape...")
    state = run_search_and_scrape(topic)

    # 3. Save the new research to ChromaDB for next time
    print("💾 Saving new research to memory...")
    vectorstore.add_texts(
        texts=[state['scraped_content']],
        metadatas=[{"topic": topic}]
    )
    
    return state

def run_search_and_scrape(topic: str) -> dict:
    """Runs Phase 1: Gathers and scrapes web data."""
    state = {}

    # Step 1 - Search
    print(f"\nStep 1 - Search agent is finding info on: {topic}")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "input": f"Find recent, reliable and detailed information about: {topic}"
    })
    state['search_results'] = search_result["output"]

    # Step 2 - Scrape
    print(f"\nStep 2 - Reader agent is scraping top resources...")
    reader_agent = build_scrape_agent()
    reader_results = reader_agent.invoke({
        "input": f"Based on the following search results about '{topic}', "
                 f"pick the most relevant URL and scrape it for deeper content.\n\n"
                 f"Search Results:\n{state['search_results'][:800]}"
    })
    state['scraped_content'] = reader_results["output"]

    return state

def run_critic(report: str) -> str:
    """Runs Phase 3: Reviews the generated report."""
    print("\n" + "="*50)
    print("Step 4 - Critic is reviewing the report")
    print("="*50)

    feedback = critic_chain.invoke({
        "report": report
    })
    
    if isinstance(feedback, dict):
        return feedback.get("text", str(feedback))
    return str(feedback)