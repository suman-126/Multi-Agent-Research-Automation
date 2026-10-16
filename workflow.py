
import os
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
from ddgs import DDGS
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# Load the API key from this project's .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Connect to the OpenRouter model
llm = ChatOpenAI(
    model="openrouter/free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2,
    max_tokens=3000,
)

# Data shared between all three agents
class ResearchState(TypedDict):
    topic: str
    research_questions: str
    research_results: str
    final_report: str


# AGENT 1: Research Planner
def research_planner(state: ResearchState):
    prompt = f"""
    You are a research planning agent.

    Research topic: {state['topic']}

    Create exactly five useful research questions.
    Focus on applications, benefits, challenges,
    future opportunities, and risks.

    Return only five numbered questions.
    Do not classify the topic as safe or unsafe.
    """

    try:
        response = llm.invoke(prompt)
        questions = str(response.content).strip()

        print("DEBUG - Planner response:", repr(questions))

        if len(questions) < 100:
            questions = (
                "1. What are the main applications of this topic?\n"
                "2. What benefits can it provide?\n"
                "3. How can it support future development?\n"
                "4. What challenges and risks exist?\n"
                "5. How can it be used responsibly?"
            )

    except Exception as e:
        print("Planner error:", str(e))
        questions = (
            "1. What are the main applications of this topic?\n"
            "2. What benefits can it provide?\n"
            "3. How can it support future development?\n"
            "4. What challenges and risks exist?\n"
            "5. How can it be used responsibly?"
        )
    return {"research_questions": questions}


# AGENT 2: Researcher
def researcher(state: ResearchState):
    print("\nResearcher Agent: Searching the web...")

    questions = state["research_questions"].splitlines()

    # Search the main topic and the first two research questions
    queries = [state["topic"]]

    for question in questions[:2]:
        cleaned_question = question.split(". ", 1)[-1].strip()
        if cleaned_question:
            queries.append(cleaned_question)

    results = []
    seen_urls = set()

    try:
        with DDGS() as search_engine:
            for query in queries:
                print(f"Searching: {query}")

                try:
                    pages = search_engine.text(
                        query,
                        max_results=3,
                    )

                    for page in pages:
                        url = page.get("href", "").strip()

                        if url and url not in seen_urls:
                            seen_urls.add(url)

                            results.append(
                                {
                                    "title": page.get(
                                        "title", "Untitled"
                                    ),
                                    "url": url,
                                    "snippet": page.get(
                                        "body", "No summary available"
                                    ),
                                }
                            )

                except Exception as e:
                    print(f"Search warning: {e}")

    except Exception as e:
        print(f"Web search error: {e}")

    if results:
        research_text = ""

        for index, result in enumerate(results, start=1):
            research_text += (
                f"\nSource {index}: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Search snippet: {result['snippet']}\n"
            )

        print(f"Researcher found {len(results)} unique sources.")

    else:
        research_text = (
            "No web search results were retrieved. "
            "Do not claim that web research was completed. "
            "Clearly state that verified sources were unavailable."
        )
        print("Researcher found no web sources.")

    return {"research_results": research_text}


# AGENT 3: Report Writer

def report_writer(state: ResearchState):
    print("\nReport Writer Agent: Creating the report...")

    prompt = f"""
    Write a concise, complete beginner-friendly research report.

    Topic: {state["topic"]}

    Research questions:
    {state["research_questions"]}

    Web research results:
    {state["research_results"]}

    Use this exact structure:
    1. Title
    2. Executive Summary (80-100 words)
    3. Five Key Findings (2-3 sentences each)
    4. Main Challenges (3-5 bullet points)
    5. Conclusion (80-100 words)
    6. Sources (list the actual source URLs provided above)

    Requirements:
    - Keep the entire report under 900 words.
    - Use only information supported by the research results.
    - Do not invent sources, facts, or URLs.
    - Finish every section, including the Sources section.
    - Return the report directly in Markdown.
    """

    try:
        response = llm.invoke(
           [
               (
                  "system",
                  "You are a professional research report writer. "
                  "Write the requested report directly. "
                  "Do not classify the topic as safe or unsafe."
               ),
               ("human", prompt),
           ]
        )
        report = str(response.content).strip()

        print("DEBUG - Writer response:", repr(report))
        print(
            "DEBUG - Writer metadata:",
            response.response_metadata
        )

        if not report:
            print("Writer returned empty content. Retrying...")

            retry_prompt = (
                "Write a short research report with a title, "
                "three key findings, a conclusion, and source URLs. "
                "Use only these research notes:\n"
                + state["research_results"][:5000]
                + "\nTopic: "
                + state["topic"]
            )

            retry_response = llm.invoke(retry_prompt)
            report = str(retry_response.content).strip()

        if not report:
            report = (
                "Report generation failed because the model "
                "returned empty responses twice. The web research "
                "results are available above. Please retry."
            )

    except Exception as e:
        print("Report Writer error:", str(e))
        report = f"Report generation failed: {e}"

    return {"final_report": report}



# Build the LangGraph workflow
graph_builder = StateGraph(ResearchState)

graph_builder.add_node("planner", research_planner)
graph_builder.add_node("researcher", researcher)
graph_builder.add_node("writer", report_writer)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "researcher")
graph_builder.add_edge("researcher", "writer")
graph_builder.add_edge("writer", END)

research_workflow = graph_builder.compile()


# Run the application
if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()

    if not topic:
        print("Please enter a research topic.")
    elif not os.getenv("OPENROUTER_API_KEY"):
        print("API key not found. Check your project's .env file.")
    else:
        result = research_workflow.invoke(
            {
                "topic": topic,
                "research_questions": "",
                "research_results": "",
                "final_report": "",
            }
        )

        print("\n" + "=" * 50)
        print("RESEARCH QUESTIONS")
        print("=" * 50)
        print(result["research_questions"])

        print("\n" + "=" * 50)
        print("WEB RESEARCH SOURCES")
        print("=" * 50)
        print(result["research_results"])

        print("\n" + "=" * 50)
        print("RESEARCH REPORT")
        print("=" * 50)
        print(result["final_report"])