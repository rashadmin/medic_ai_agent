# medic_ai_agent

> An AI-powered agent providing immediate first-aid guidance and relevant resources for medical emergencies.

## 🧠 Overview

This project is an AI-powered medical assistant agent, designed to provide immediate first-aid guidance based on user-described medical emergencies. It leverages large language models (LLMs) to process natural language input, extract critical information, and deliver relevant, structured first-aid instructions, along with supplementary resources like instructional YouTube videos. The agent aims to be a quick reference tool in emergency situations, helping users understand symptoms and appropriate initial responses.

## 🔨 What I Built

I built a conversational AI agent that acts as a first-aid guide. Its core features include:

- **Intelligent Information Extraction**: Processes user descriptions of medical situations to identify emergency names, symptoms, and relevant first-aid keywords.
- **Knowledge Base Integration**: Scrapes and utilizes first-aid information from trusted sources like Mayo Clinic and Red Cross websites to provide accurate guidance.
- **Structured First-Aid Instructions**: Delivers clear, step-by-step first-aid instructions, tailored to the identified emergency.
- **Multimedia Support**: Integrates with the YouTube Data API to suggest relevant video tutorials for visual aid, filtering them by appropriate duration.
- **Contextual Understanding**: Maintains conversational context to provide coherent and evolving advice.
- **Human-in-the-Loop**: Allows for user confirmation or additional input at critical junctures in the decision-making process.
- **Potential Hospital Integration**: Includes functionality to interface with location-based services (Geoapify) to potentially locate nearby hospitals, though the full implementation details for alerts are not explicit.

## 💭 Thought Process

My approach involved creating a robust agentic workflow using LangGraph, which allowed me to orchestrate complex interactions between the LLM, external tools, and dynamic state management. I decided to use Pydantic models extensively to enforce structured outputs from the LLM, which is crucial for reliably extracting sensitive medical information and ensuring the agent's actions are based on well-defined data.

A key design decision was to separate the concerns of keyword extraction, document retrieval, and information extraction into distinct, manageable steps. This modularity makes the agent more maintainable and easier to debug. For instance, `firstaidkeywords.py` is dedicated solely to scraping keywords, while `getdocuments.py` handles fetching and cleaning content based on those keywords.

Web scraping was a necessary component to build a dynamic knowledge base from authoritative sources. I chose `requests` and `BeautifulSoup` for this, implementing domain-specific parsing logic for Mayo Clinic and Red Cross due to their differing HTML structures. This highlights a trade-off: while effective, web scraping makes the agent susceptible to changes in website layouts.

Integrating external APIs like YouTube and Geoapify was central to providing rich, actionable advice. For YouTube, I implemented post-search filtering to ensure only relevant and appropriately-timed videos are suggested, addressing a limitation of the API's direct search capabilities.

Finally, incorporating human feedback using `langgraph.types.interrupt` was a deliberate choice to build a safer agent, especially in the context of medical advice. This allows the user to validate or refine the agent's understanding before critical information is provided.

## 🛠️ Tools & Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Agent Framework** | LangGraph |
| **LLM Orchestration** | LangChain |
| **AI / LLM** | Google Gemini 2.5 Flash |
| **Data Validation** | Pydantic |
| **Web Scraping** | `requests`, `BeautifulSoup4` |
| **Asynchronous Operations** | `anyio`, `asyncio` |
| **External APIs** | YouTube Data API, Geoapify |
| **Message Queuing** | Redis |
| **Testing** | `pytest` |
| **Observability** | LangSmith |
| **Utilities** | `typing_extensions`, `dataclasses`, `os`, `json`, `sys`, `isodate`, `datetime` |

## 🚀 Getting Started

### Prerequisites
- Python >= 3.10
- Google Gemini API Key
- YouTube Data API Key
- Geoapify API Key
- Redis server (for message queuing)

### Installation

```bash
git clone https://github.com/rashadmin/medic_ai_agent.git
cd medic_ai_agent
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory and populate it with your API keys and other configurations:

```env
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
GEOAPIFY_API_KEY=your_geoapify_api_key_here
REDIS_URL=redis://localhost:6379/0 # Or your Redis connection string
LANGSMITH_TRACING=true # Optional, for LangSmith tracing
LANGCHAIN_API_KEY=your_langsmith_api_key # Optional, if LANGSMITH_TRACING is true
```

### Run

The primary entry point for the agent's graph is within `src/agent/graph.py`. You would typically run an application that imports and invokes this graph. A simplified example for direct invocation might look like:

```python
# This is a conceptual example based on the code structure,
# the actual main execution script might vary.
from src.agent.graph import graph

async def main():
    # Example invocation with a user message
    config = {"configurable": {"thread_id": "some_unique_thread_id"}}
    user_message = "I have a severe headache, nausea, and sensitivity to light."
    inputs = {"messages": [("user", user_message)]}
    result = await graph.ainvoke(inputs, config)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 📖 Usage

### Example 1: Providing First-Aid Guidance

The agent is designed to receive a user's description of a medical situation and respond with relevant first-aid steps.

**User Input:**
```
"My friend just collapsed and is not breathing. What should I do?"
```

**Agent Output (Conceptual):**
```
First Aid for Unresponsive and Not Breathing:

1. Call Emergency Services: Immediately call your local emergency number (e.g., 911).
2. Start CPR: If you are trained, begin chest compressions immediately.
   - Place the heel of one hand in the center of the person's chest.
   - Place your other hand on top of the first, interlocking your fingers.
   - Push hard, at least 2 inches (5 cm) deep, at a rate of 100 to 120 compressions per minute.
   - Continue until emergency responders arrive or the person shows signs of life.

Consider checking for a YouTube video tutorial for CPR:
- [Link to CPR video 1]
- [Link to CPR video 2]
```

### Example 2: Human Intervention for Symptom Confirmation

If the agent needs clarification or confirmation on symptoms, it can pause and prompt the user.

**Agent's Prompt (Conceptual):**
```
I've identified "severe headache", "nausea", and "sensitivity to light". Are these the main symptoms, or are there others? Please confirm or provide additional details.
```

**User Input:**
```
"Yes, those are correct. Also, I'm seeing flashing lights."
```

**Agent's Subsequent Action:**
The agent would incorporate "flashing lights" into its understanding and proceed with updated information extraction.

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) — Agent framework
- [LangChain Documentation](https://python.langchain.com/docs/get_started/) — LLM orchestration
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) — Data validation
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) — HTML parsing
- [requests Library Documentation](https://requests.readthedocs.io/en/latest/) — HTTP requests
- [Google API Client Library for Python](https://developers.google.com/api-client-library/python/start/installation) — Interacting with Google APIs (e.g., YouTube)
- [Geoapify Documentation](https://www.geoapify.com/docs) — Location-based services
- [Redis Documentation](https://redis.io/docs/) — Message queuing
- [Pytest Documentation](https://docs.pytest.io/en/stable/) — Testing framework
- [AnyIO Documentation](https://anyio.readthedocs.io/en/stable/) — Asynchronous I/O

## 📄 License

MIT © [rashadmin](https://github.com/rashadmin)
