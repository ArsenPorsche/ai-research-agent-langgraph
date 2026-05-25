# AI Research Agent (LangGraph)

An autonomous AI research assistant built with **LangGraph**, **LangChain**, and **Streamlit**. The agent performs iterative web searches, synthesizes information into Markdown reports, and undergoes a self-critique process to ensure factual accuracy.

## 🚀 Overview

The AI Research Agent follows a sophisticated iterative workflow:
1.  **Researcher**: Searches the web using **Tavily API** for relevant information.
2.  **Writer**: Drafts a comprehensive report based on collected sources.
3.  **Critic**: Evaluates the report for accuracy and completeness. If necessary, it triggers another research cycle or a rewrite.

## ✨ Key Features

-   **Autonomous Workflow**: Utilizes state graphs to manage complex agentic cycles (Researcher -> Writer -> Critic).
-   **Self-Correction**: An integrated critic node identifies missing info or errors, forcing the agent to adapt its search strategy.
-   **Real-time Web Search**: Integrated with **Tavily** for high-quality, AI-optimized search results.
-   **Streamlit UI**: A clean, interactive dashboard to monitor agent logs and view the final report.
-   **Tracing**: Built-in support for **LangSmith** to monitor and debug agentic traces.

## 🛠️ Tech Stack

-   **Python**
-   **LangGraph** (Orchestration and state management)
-   **LangChain** (LLM framework)
-   **OpenAI GPT-4o-mini** (Underlying LLM)
-   **Tavily** (Search engine for AI)
-   **Streamlit** (User interface)

## 📂 Project Structure

```text
.
├── app.py              # Streamlit application entry point
├── requirements.txt    # Project dependencies
└── src/
    └── agent/
        ├── config.py   # Tool and LLM configuration
        ├── graph.py    # LangGraph state machine definition
        ├── nodes.py    # Implementation of Researcher, Writer, and Critic logic
        ├── prompts.py  # System prompts for different agent roles
        └── state.py    # Type definitions for the agent's state
```

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/ArsenPorsche/ai-research-agent-langgraph.git
cd qabot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets
The application uses Streamlit secrets for configuration. Create a `.streamlit/secrets.toml` file in the root directory:

```toml
OPENAI_API_KEY = "your_openai_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
LANGSMITH_API_KEY = "your_langsmith_api_key"
LANGSMITH_TRACING = "true"
```

### 4. Run the Application
```bash
streamlit run app.py
```

## 🔄 How it Works

The agent logic is defined in `src/agent/graph.py`. It uses a `StateGraph` where:
-   The **Researcher** node uses `TavilySearch` to fetch data.
-   The **Writer** node uses `GPT-4o-mini` to synthesize a Markdown report.
-   The **Critic** node uses structured output to decide whether the report is finished or requires more work.
-   A maximum of **3 iterations** is enforced to ensure the process terminates.

## 📝 License
This project is licensed under the MIT License.
