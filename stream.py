import os
import re
import html
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load the existing .env file
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=PROJECT_DIR / ".env")

# Import the existing LangGraph workflow
from workflow import research_workflow

# PAGE CONFIGURATION
st.set_page_config(
    page_title="AI ResearchFlow",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# CUSTOM UI STYLING
st.markdown(
    """
    <style>
    /* Main application background */
    .stApp {
        background-color: #f5f7fc;
        color: #17233f;
    }

    /* Main content spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Dark navy sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #101a35 0%, #17294d 100%
        );
        border-right: 1px solid #26385c;
    }

    [data-testid="stSidebar"] * {
        color: #edf2ff;
    }

    [data-testid="stSidebar"] hr {
        border-color: #35486d;
    }

    /* Headings */
    h1, h2, h3 {
        color: #14213d;
    }

    /* Sidebar branding */
    .brand-title {
        font-size: 25px;
        font-weight: 750;
        color: #ffffff;
        letter-spacing: -0.6px;
    }

    .brand-subtitle {
        color: #b9c8e8;
        font-size: 13px;
        line-height: 1.6;
    }

    /* Hero section */
    .hero {
        padding: 26px;
        border-radius: 18px;
        background: linear-gradient(
            120deg, #15264b 0%, #244f91 100%
        );
        color: white;
        margin-bottom: 24px;
    }

    .hero h2 {
        color: white;
        margin-bottom: 8px;
        font-size: 29px;
    }

    .hero p {
        color: #e0eaff;
        font-size: 15px;
        margin-bottom: 0;
        line-height: 1.7;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f4;
        border-radius: 14px;
        padding: 18px;
        min-height: 100px;
        box-shadow: 0 3px 12px rgba(20, 40, 80, 0.04);
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 9px;
    }

    .metric-value {
        color: #173b79;
        font-size: 23px;
        font-weight: 750;
    }

    /* Input fields */
    [data-testid="stTextInput"] input {
        border-radius: 10px;
        border-color: #d7e0ef;
        min-height: 45px;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        background: #2563eb;
        color: white;
        border: 1px solid #2563eb;
        border-radius: 10px;
        min-height: 43px;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #1d4ed8;
        border-color: #1d4ed8;
        color: white;
    }

    /* Expanders and tabs */
    [data-testid="stExpander"] {
        background: white;
        border: 1px solid #e2e8f4;
        border-radius: 12px;
    }

    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        color: #64748b;
        font-size: 12px;
        padding-top: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# SESSION STATE
if "research_output" not in st.session_state:
    st.session_state.research_output = None

if "research_topic" not in st.session_state:
    st.session_state.research_topic = ""


# SIDEBAR
with st.sidebar:
    st.markdown(
        """
        <div class="brand-title">🔬 ResearchFlow</div>
        <div class="brand-subtitle">
            AI-powered research workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Workspace")
    st.caption("Your research pipeline")

    st.markdown("🔹 Research Planner")
    st.markdown("🔹 Web Researcher")
    st.markdown("🔹 Report Writer")

    st.divider()

    st.markdown("### About")
    st.caption(
        "Transform a research topic into a structured "
        "report using a multi-agent LangGraph workflow."
    )

    st.markdown("### Technology")
    st.caption("LangGraph · OpenRouter · Streamlit")
    st.caption("DuckDuckGo · LangChain")

    st.divider()

    if st.button(
        "＋ New Research",
        use_container_width=True,
    ):
        st.session_state.research_output = None
        st.session_state.research_topic = ""
        st.rerun()

# MAIN HEADER
st.markdown(
    """
    <div class="hero">
        <h2>Discover insights with AI</h2>
        <p>
            Enter a topic, explore web sources, and generate
            a structured research report with your AI agents.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Start your research")
st.caption(
    "Describe the topic you want to investigate. "
    "Your research agents will handle the workflow."
)


# RESEARCH INPUT

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        value=st.session_state.research_topic,
        placeholder="e.g. How can AI improve healthcare?",
        help="Enter a clear topic for better research results.",
    )

    submitted = st.form_submit_button(
        "🚀 Run Research",
        use_container_width=True,
    )

# RUN EXISTING LANGGRAPH WORKFLOW
if submitted:

    if not topic.strip():
        st.warning("Please enter a research topic.")

    elif not os.getenv("OPENROUTER_API_KEY"):
        st.error(
            "OpenRouter API key not found. "
            "Please check your local .env file."
        )

    else:
        topic = topic.strip()

        # Keep the same state keys used by workflow.py
        research_state = {
            "topic": topic,
            "research_questions": "",
            "research_results": "",
            "final_report": "",
        }

        st.markdown("## Research progress")

        progress_bar = st.progress(0)
        progress_text = st.empty()

        # The compiled graph streams updates after each node.
        # The actual planner, researcher, and writer are unchanged.
        node_details = {
            "planner": (
                33,
                "Research Planner",
                "Generating research questions...",
            ),
            "researcher": (
                66,
                "Researcher Agent",
                "Searching the web and collecting sources...",
            ),
            "writer": (
                100,
                "Report Writer",
                "Preparing your final report...",
            ),
        }

        try:
            with st.status(
                "Starting your research workflow...",
                expanded=True,
            ) as status:

                for update in research_workflow.stream(
                    research_state,
                    stream_mode="updates",
                ):

                    # Merge each node's returned state updates
                    for node_name, node_output in update.items():

                        if isinstance(node_output, dict):
                            research_state.update(node_output)

                        if node_name in node_details:
                            percent, agent_name, message = (
                                node_details[node_name]
                            )

                            progress_bar.progress(percent)

                            progress_text.markdown(
                                f"**{percent}% — {agent_name}**  \n"
                                f"{message}"
                            )

                            status.write(
                                f"✓ {agent_name} completed"
                            )

                status.update(
                    label="Research completed successfully!",
                    state="complete",
                    expanded=False,
                )

            progress_bar.progress(100)
            progress_text.success("All three agents have finished.")

            # Preserve the same result/session-state keys
            st.session_state.research_output = research_state
            st.session_state.research_topic = topic

            st.success("Your research report is ready!")

        except Exception as error:
            progress_text.empty()

            st.error(
                "The research workflow could not be completed. "
                "Please check the terminal for the detailed error."
            )

            # Keep technical details available for debugging
            with st.expander("Technical error details"):
                st.code(str(error))


# DISPLAY RESEARCH RESULTS
result = st.session_state.research_output

if result:

    st.divider()

    st.markdown("## Your research results")

    st.markdown(
        f"**Topic:** {st.session_state.research_topic}"
    )

    research_questions = result.get(
        "research_questions", ""
    )

    research_results = result.get(
        "research_results", ""
    )

    final_report = result.get(
        "final_report", ""
    )

    # Count web URLs in the collected research text
    source_count = len(
        set(
            re.findall(
                r"https?://[^\s<>\"')\]]+",
                research_results,
            )
        )
    )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Research Agents</div>
                <div class="metric-value">3</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Research Questions</div>
                <div class="metric-value">5</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Web Sources Found</div>
                <div class="metric-value">{source_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Separate result sections
    questions_tab, sources_tab, report_tab = st.tabs(
        [
            "🧠 Research Questions",
            "🌐 Web Sources",
            "📄 Final Report",
        ]
    )

    with questions_tab:
        st.markdown("### Questions generated by the Planner")

        if research_questions:
            st.markdown(research_questions)
        else:
            st.info("No research questions were returned.")

    with sources_tab:
        st.markdown("### Collected web research")

        if research_results:
            st.markdown(research_results)
        else:
            st.info("No web research results were returned.")

    with report_tab:
        st.markdown("### Your completed report")

        if final_report:
            st.markdown(final_report)

        if final_report:
            # Clean Markdown formatting for the downloaded file
            download_report = html.unescape(final_report)
            download_report = download_report.replace("\u00a0", " ")

            # Fix common escaped Markdown characters
            download_report = download_report.replace(r"\*\*", "**")
            download_report = download_report.replace(r"\*", "*")
            download_report = download_report.replace(r"\#", "#")
            download_report = download_report.replace(r"\-", "-")

            # Remove bold formatting wrapped around Markdown headings
            download_lines = []

            for line in download_report.splitlines():
                stripped = line.strip()

                if stripped.startswith("**#") and stripped.endswith("**"):
                    stripped = stripped[2:-2].strip()

                download_lines.append(stripped if stripped else "")

            download_report = "\n".join(download_lines)

            st.download_button(
                label="⬇️ Download Research Report",
                data=download_report,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.warning("The workflow did not return a final report.")

# FOOTER
st.markdown(
    """
    <div class="app-footer">
        AI ResearchFlow · Built with LangGraph and Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)