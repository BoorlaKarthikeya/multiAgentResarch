import streamlit as st 
from swarm import Swarm , Agent
from duckducukgo_search import DDGS
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MODEL = "llama3.2"
client = Swarm()

ddgs = DDGS()

agent1_role = """Your role is to gather latest news articles on specified topics using DuckDuckGo's search capabillities."""


def search_web(query) :
    print(f"searching the web for {query}........")

    current_date = datetime.now().strftime("%Y-%m")
    results = ddgs.text(f"{query} {current_date}" , max_results = 10)
    
    if results:
        web_results = ""
        for result in results :
            web_results += f"Title : {result['title']}\n"
            web_results += f"Link : {result['href']}\n"
            web_results += f"nDescription : {result['body']}\n\n"
    
    return web_results.strip()


web_search_agent = Agent(
    name="Web Search Agent",
    instructions = agent1_role,
    functions = [search_web],
    model = MODEL
)

research_agent = Agent(
    name = 'Research Agent',
    Instructions = """Your role is to analyze and synthesize the raw search results. You should :
    1. Remove duplicate information and redundant content
    2. Identify and merge related topics and themes
    3. Verify information consistency across sources
    4. Prioritize recent and relevant information
    5. extract key facts , statistics , and quotes
    6. Identify primary sources when available
    7. Flag any contradictory information
    8. Maintain proper attribution in a logical sequence
    9. Organize information in a logical sequence
    10. Preserve important context and realationships between topics.
    """,
    model = MODEL

)


writer_agent = Agent(
    name = 'writer Assistant',
    instructions = """Your role is to transform the duplicated research results into a polished , publication ready article. You should :
    1. Organize content into clear , thematic actions
    2.Write in a professional yet engaging tone
    3. Ensure proper flow between topics
    4. Add relevant context where needed 
    5. Maintain factual accuracy while making complex topics accesible
    6. Include a brief summary at the begining
    7. Format with clear headlines and subheadings
    8. Preserve all key information from the source material.
    """,
    model = MODEL

)

def run_workflow(query) :
    print("Running web research assistant workflow....")

    news_response = client.run(
        agent = web_search_agent,
        message = [{"role" : "user" , "content" : f"search the web for {query}"}],
    )
    raw_news = news_response.messages[-1]['content']

    research_analysis_response = cilent.run(
        agent = research_agent,
        messages = [{"role" : "user" , "content" : raw_news}],

    )
    duplicated_news = research_analysis_response.messages[-1]['content']

    publication_response = client.run(
        agent = writer_agent,
        messages = [{"role" : "user" , "content" : duplicated_news}],
    )
    return publication_response.messages[-1]['content']


def main():
    st.set_page_config(page_title="Internet Research Assistant 🔎", page_icon="🔎")
    st.title("Internet Research Assistant 🔎")

    # Initialize session state for query and article
    if 'query' not in st.session_state:
        st.session_state.query = ""
    if 'article' not in st.session_state:
        st.session_state.article = ""

    # Create two columns for the input and clear button
    col1, col2 = st.columns([3, 1])

    # Search query input
    with col1:
        query = st.text_input("Enter your search query:", value=st.session_state.query)

    # Clear button
    with col2:
        if st.button("Clear"):
            st.session_state.query = ""
            st.session_state.article = ""
            st.rerun()

    # Generate article only when button is clicked
    if st.button("Generate Article") and query:
        with st.spinner("Generating article..."):
            # Get streaming response
            streaming_response = run_workflow(query)
            st.session_state.query = query
            
            # Create a placeholder for the streaming text
            message_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            for chunk in streaming_response:
                # Skip the initial delimiter
                if isinstance(chunk, dict) and 'delim' in chunk:
                    continue
                    
                # Extract only the content from each chunk
                if isinstance(chunk, dict) and 'content' in chunk:
                    content = chunk['content']
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            # Update final response
            message_placeholder.markdown(full_response)
            st.session_state.article = full_response

    # Display the article if it exists in the session state
    if st.session_state.article:
        st.markdown(st.session_state.article)


if __name__ == "__main__":
    main()



