# AI Agent for Media Analysis

This project is an autonomous AI agent that acts like a junior media analyst.

Instead of dashboards or static queries, you ask questions in plain English like:

“Which channel had the best ROI last quarter?”

And the agent:

- decides what data it needs
- queries BigQuery safely
- returns clear, actionable insights

---

## Architecture

The agent operates in a **ReAct loop** (Reason → Act → Observe) orchestrated by LangGraph.

The key design decision was to keep the LLM responsible only for reasoning and language, delegating all data access to typed Python tools. This avoids the common mistake of pushing SQL results directly into the prompt and hoping the model interprets them correctly.

The architecture follows the **LLM-as-Controller** pattern, where the model decides which tools to use while execution happens in deterministic code.

```
User question
        │
        ▼
  FastAPI /chat
        │
        ▼
  LangGraph Agent  ──── decides ────►  tool_get_traffic_volume
   (gpt-4o-mini)                          └─ COUNT on users, filtered by
        │                                     traffic_source + date range
        │            ──── decides ────►  tool_get_channel_performance
        │                                  └─ JOIN users + orders + order_items
        │                                     (excludes cancelled/returned orders)
        ▼
  Analytical response in natural language
```

### Why LangGraph instead of pure LangChain?

LangGraph models the agent as an explicit state machine, making the tool-calling loop inspectable and easy to evolve. Adding a new tool or a conditional branch (e.g., “if revenue data is missing, use only traffic volume”) becomes an edge in the graph—not a callback buried in the code.

### Tools

| Tool                     | When it is triggered                                 | Executed Query                                                             |
| ------------------------------ | ------------------------------------------------- | --------------------------------------------------------------------------- |
| `tool_get_traffic_volume`      | Questions about user volume, top of funnel | `COUNT` on `users`, pparameterized by `traffic_source` and date              |
| `tool_get_channel_performance` | ROI, revenue, channel ranking                   | `JOIN users + orders + order_items`, filters status `cancelled` and `returned` |

Both tools extract the date range directly from the user’s question (via LLM) and pass it as parameters to BigQuery, without string interpolation—eliminating SQL injection risk.

---

## Project Structure

```
.
├── main.py                   # FastAPI app, routes, and Pydantic typing
├── agent/
│   ├── bot.py                # LangGraph definition and agent persona
│   └── tools.py              # Tools exposed to the AI (@tool)
├── database/
│   └── bigquery_client.py    # GCP connection and parameterized SQL queries
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables (ignored in git)
└── .env.example              # Example environment variables
```

---

## Agent Interface (Cleytinho)

![Interface do Analista de Mídia Cleytinho](cleytinho.png)

*(Interface built with Streamlit consuming the LangGraph API)*


## Setup

**Prerequisites:** Python 3.10+, a GCP account with read access to BigQuery (free tier is sufficient), and an OpenAI API Key.

### 1. Clone and install dependencies

```bash
git clone https://github.com/taisbronca/case_monks.git
cd case_monks
python3 -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Credentials

Place your GCP service account JSON file in the project root (e.g., `gcp-key.json`).
Create the `.env` file from the example included in the repository:

```bash
cp .env.example .env
```

Fill in the `.env`:

```
GOOGLE_APPLICATION_CREDENTIALS="./gcp-key.json"
OPENAI_API_KEY="sk-..."
```

The service account must have the permissions `roles/bigquery.user` and `roles/bigquery.dataViewer` in the `bigquery-public-data` project.

### 3. Run the Application

The architecture includes two services that must run simultaneously: the API (Backend) and the Visual Interface (Frontend).

**Terminal 1 (Backend - FastAPI):**
Start the main server, which will process the AI and connect to the database:

```bash
uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000 (with interactive docs at /docs).

**Terminal 2 (Frontend - Streamlit):**
The interface was built with Streamlit to quickly demonstrate the agent’s value in a product-like context, allowing analysts to interact with the system without directly accessing the API.

Open a new terminal tab, activate the virtual environment (source venv/bin/activate), and run the chat UI:

```bash
streamlit run frontend.py
```

The Agent interface will automatically open in your browser at http://localhost:8501.

## Usage Examples

You can interact with the Agent in two ways:

Option A: Graphical Interface (Recommended)
Acess http://localhost:8501 and type your questions in natural language directly into the chat.

Option B: API (cURL or Swagger)
Send a POST request to the /chat endpoint with the question in the request body:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "What was the revenue performance of media channels in January 2024?"}'
```

How the Agent processes it:
Upon receiving the question, the agent will: extract the time period, trigger the tool_get_channel_performance tool, safely join the three tables in BigQuery, and return a ranked analysis with revenue and order volume per channel.

Other example questions the agent can answer:

- "What was the volume of users coming from Search last quarter?"
- "Which channel has the best ROI and why?"
- "Compare the performance of Facebook and Email in 2023."

---

## Dataset

Uses the public BigQuery dataset `bigquery-public-data.thelook_ecommerce`. The `traffic_source` column in the `users` table is treated as a proxy for media channels (Search, Organic, Facebook, Email, Display).

---

## MVP Limitations

This MVP was built to demonstrate an agent architecture with tool calling.

Possible improvements:

- Add query caching to reduce BigQuery costs
- Support for multiple metrics (CAC, LTV, conversion)
- Use of a Vector DB for analytical memory
- Serverless deployment on Cloud Run

---
## Next Steps

If evolved into production, the agent could:

- Integrate directly with media APIs (Google Ads, Meta Ads)
- Run automated daily analyses
- Generate performance alerts
- Create automated reports for managers
