# LLM-agent: Automated Mental-Health LLM Research Agent

LLM-agent is an automated tool that collects the latest information about **LLM-based applications in mental health**, including updates from scientific articles, books, news websites, and blog posts. The agent processes and filters relevant content and can optionally send updates to a personal Telegram chat.

## Features

* Automatic crawling of LLM/AI news related to mental health
* Text preprocessing and cleaning
* Detection of relevant topics using NLP and LLM-based filters
* Summary extraction and keyword generation
* Optional Telegram delivery
* Modular architecture suitable for extension and research use

## Project Structure

```
LLM-agent/
│
├── src/                 # Source code
├── data/                # Collected news and articles
├── logs/                # Agent logs
├── requirements.txt     # Dependencies
├── config/              # Settings (API keys should not be uploaded)
└── README.md            # Documentation
```

## How It Works

1. The agent fetches new information from selected online sources.
2. Text is cleaned and normalized.
3. NLP/LLM modules extract relevant insights about mental-health-related LLM applications.
4. Results can be stored locally or delivered to Telegram.

## Installation

```bash
git clone https://github.com/Farzanehlashgari/LLM--agent.git
cd LLM--agent
pip install -r requirements.txt
```

## Running the Agent

```bash
python src/main.py
```

If using Telegram notifications, add your bot token and chat ID to:

```
config/telegram_config.json
```

## Research Context

This project supports ongoing research in:

* LLM applications in mental health
* automated information gathering
* emotion-aware and safety-focused agents
* multi-agent LLM systems

## License

MIT License.

## Contact

**Farzaneh Lashgari** and **Anilson Monteiro**
PhD Researcher – AI, NLP, Mental Health Technologies
NOVA LINCS / UBI
