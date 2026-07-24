<h1 align="center" style="border-bottom: none">
<img alt="Voice Satellite - LLM Tools" src="https://raw.githubusercontent.com/jxlarrea/voice-satellite-card-llm-tools/refs/heads/main/assets/banner.png" width="650" />
</h1>

<p align="center">
<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=jxlarrea&repository=voice-satellite-card-llm-tools"><img src="https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge" alt="hacs_badge"></a>
<a href="https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases"><img src="https://img.shields.io/github/downloads/jxlarrea/voice-satellite-card-llm-tools/total?style=for-the-badge&label=Downloads&color=blue" alt="Downloads"></a>
<a href="https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases"><img src="https://shields.io/github/v/release/jxlarrea/voice-satellite-card-llm-tools?style=for-the-badge&color=purple" alt="version"></a>
<a href="https://github.com/jxlarrea/voice-satellite-card-llm-tools/actions/workflows/release.yml"><img src="https://img.shields.io/github/actions/workflow/status/jxlarrea/voice-satellite-card-llm-tools/release.yml?style=for-the-badge&label=Build" alt="Build"></a>
</p>

<p align="center">
<a href="https://buymeacoffee.com/jxlarrea"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

Extend your voice assistant's capabilities with **web, Wikipedia, image, video search, weather forecast, and financial data tools** for Home Assistant's LLM integrations. When paired with the [Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration), results are displayed directly in the card UI.

## Screenshot

![Screenshot](https://github.com/user-attachments/assets/621ee33f-83db-45ec-83ef-39038008e7dc)

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
  - [Web Search](#web-search)
  - [Wikipedia](#wikipedia)
  - [Image Search](#image-search)
  - [Video Search](#video-search)
  - [Weather Forecast](#weather-forecast)
  - [Financial Data](#financial-data)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Provider Setup](#provider-setup)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)

## How It Works

This integration registers **LLM API tools** with Home Assistant. When a conversation agent (OpenAI, Google Generative AI, Anthropic, Ollama, etc.) receives a request, it can call these tools to fetch results. The [Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration) renders the results visually.

**Example voice commands:**

- "Search the web for best restaurants in Tokyo"
- "Tell me about Marie Curie"
- "Show me pictures of golden retrievers"
- "Search for videos on how to make sourdough bread"
- "What's the weather like tomorrow?"
- "What's the price of Apple stock?"
- "How much is Bitcoin right now?"
- "Convert 100 USD to EUR"

> **Requires the [Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration).** Without it, the tools still return data to the conversation agent but there will be no visual display.

## Features

### Web Search

Search the web using [Brave Search API](https://brave.com/search/api/) or a self-hosted [SearXNG](https://docs.searxng.org/) instance. Returns page titles, snippets, and thumbnails. The conversation agent synthesizes results into a concise answer.

### Wikipedia

Look up topics on Wikipedia — no API key required. Returns a single authoritative article with thumbnail. Choose between **Concise** (1-3 sentence summary) or **Detailed** (full introduction section, uses more LLM tokens).

### Image Search

Search for images using [Brave Search API](https://brave.com/search/api/) or [SearXNG](https://docs.searxng.org/). Supports SafeSearch (Brave) and configurable result counts (1-10).

### Video Search

Search YouTube via the [YouTube Data API v3](https://developers.google.com/youtube/v3). Returns titles, thumbnails, channel names, durations, and view counts.

### Weather Forecast

![Weather](https://github.com/user-attachments/assets/5c439e57-3047-4457-a18a-f8dbb778e1f7)

Get weather forecasts using your existing Home Assistant weather entities — no additional API key required. Supports today, tomorrow, specific days of the week, and weekly outlooks. Optionally include hour-by-hour detail, current temperature, and humidity readings from dedicated sensors. Weather condition icons are displayed alongside forecast data.

### Financial Data

![Stocks](https://github.com/user-attachments/assets/20f66567-7e9c-4d69-af7d-cad699c6149e)

Look up stock prices, cryptocurrency prices, and convert currencies using [Finnhub](https://finnhub.io/) (free tier available). Stocks return current price, daily change, high/low, and company logo. Cryptocurrency queries (BTC, ETH, DOGE, and 25+ others) are automatically resolved via [CoinGecko](https://www.coingecko.com/) for accurate pricing. Currency conversion supports all major forex pairs.

### Auto Display / Auto Play

When the user asks for something specific (e.g. "show me the Mona Lisa"), the card automatically displays the first result. For broader searches, results appear as a browsable list.

### Result Caching

Search results (web, image, video, Wikipedia) are cached in memory (default: 1 hour). Repeated queries return instantly without consuming API quota. Weather and financial data are fetched live on every request.

## Prerequisites

1. **[Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration)** installed and configured
2. A **conversation agent** with LLM tool support (OpenAI, Google Generative AI, Anthropic, Ollama, etc.)
3. **API credentials** for your chosen providers (Wikipedia and Weather require none)

## Installation

### HACS (Recommended)

Voice Satellite LLM Tools is available in [HACS](https://hacs.xyz/). Use the link below to open the HACS repository in Home Assistant.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jxlarrea&repository=voice-satellite-card-llm-tools)

Or search for `Voice Satellite LLM Tools` in the HACS default repository.

### Manual

1. Download the [latest release](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases/latest)
2. Copy `custom_components/voice_satellite_llm_tools` to your `config/custom_components/` directory
3. Restart Home Assistant

## Setup

Each tool is configured as a separate entry via **Settings > Devices & Services > Add Integration > Voice Satellite LLM Tools**. After adding a tool, enable its LLM API in your assistant pipeline. Go to **Settings > Voice Assistants**, select your pipeline, and click the gear icon next to **Conversation Agent**. From there, select the newly added tools under **Tool Providers** or **Control Home Assistant** (depending on your conversation integration).

| Tool | Setup Steps |
|------|-------------|
| **Web Search** | Select provider (Brave/SearXNG) → enter credentials → configure max results |
| **Wikipedia** | Choose detail level (Concise/Detailed) |
| **Image Search** | Select provider (Brave/SearXNG) → enter credentials → configure max results |
| **Video Search** | Enter YouTube Data API v3 key → configure max results |
| **Weather Forecast** | Select daily weather entity → optionally add hourly entity, temperature, and humidity sensors |
| **Financial Data** | Select provider (Finnhub) → enter API key |

> Only one entry per tool type is allowed. Use **Configure** to change settings, or remove the entry to disable a tool.

## Provider Setup

### Brave Search

1. Sign up at the [Brave Search API](https://brave.com/search/api/) page (free tier available)
2. Copy your API key — the same key works for both Web Search and Image Search

### SearXNG

1. Set up a [SearXNG](https://docs.searxng.org/) instance with **JSON format** enabled
2. Note the instance URL (e.g., `http://localhost:8080`)
3. Optionally specify engines (e.g., `google,bing` for web or `bing images,google images` for images)

### YouTube Data API v3

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **YouTube Data API v3** and create an API key

### Wikipedia

No setup required — uses the public Wikipedia API.

### Finnhub

1. Sign up at [Finnhub](https://finnhub.io/) (free tier: 60 calls/min)
2. Copy your API key from the dashboard

### Weather Forecast

No API key required — uses your existing Home Assistant weather entities. You need at least one weather integration configured (e.g., Met.no, OpenWeatherMap, AccuWeather).

## Configuration Options

| Tool | Option | Description |
|------|--------|-------------|
| **Web Search** | Provider | Brave or SearXNG |
| | API Key | Brave only |
| | Server URL | SearXNG only |
| | Engines | SearXNG only — comma-separated list |
| | Max Results | 1-6 (default: 3) |
| **Wikipedia** | Article Detail | Concise (short summary) or Detailed (full intro, more tokens) |
| **Image Search** | Provider | Brave or SearXNG |
| | API Key | Brave only |
| | Server URL | SearXNG only |
| | Engines | SearXNG only — comma-separated list |
| | SafeSearch | Brave only — off, moderate, or strict |
| | Max Results | 1-10 (default: 3) |
| **Video Search** | YouTube API Key | Your API key |
| | Max Results | 1-6 (default: 3) |
| **Weather Forecast** | Daily Forecast Entity | A weather entity that provides daily forecasts (required) |
| | Hourly Forecast Entity | Enables hour-by-hour detail for specific days (optional) |
| | Current Temperature Sensor | Includes current temperature in today's/weekly forecast (optional) |
| | Current Humidity Sensor | Includes current humidity in today's/weekly forecast (optional) |
| **Financial Data** | Provider | Finnhub |
| | Finnhub API Key | Your API key from [finnhub.io](https://finnhub.io/) |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Assistant doesn't search | Ensure you're using a conversation agent with LLM tool support (not the built-in HA agent). Verify the LLM APIs are enabled in your Assist pipeline settings. |
| No results returned | Check API quotas, verify SearXNG is reachable, or try a different query. |
| Results don't display | Ensure the [Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration) is installed and up to date. |
| Weather returns no forecast | Verify your weather entity supports daily forecasts. Check **Developer Tools > States** to confirm the entity has forecast data. |
| Stock price not found | Ensure you're using the correct ticker symbol (e.g., `AAPL` not `Apple`). For crypto, use the coin symbol (e.g., `BTC`, `ETH`). |
| Crypto shows wrong price | Some crypto symbols overlap with stock tickers. The tool prioritizes crypto for known symbols (BTC, ETH, etc.) and falls back to stocks otherwise. |

## License

MIT License - see [LICENSE](LICENSE) for details.


---

## ⚡ LLM Tools+ fork (alarms)

This is a fork of [`jxlarrea/voice-satellite-card-llm-tools`](https://github.com/jxlarrea/voice-satellite-card-llm-tools) with a voice-announced **Alarms** tool (domain `voice_satellite_llm_tools_plus`, so it can run alongside the original).

It exposes `stop_alarm` / `snooze_alarm` services (also reachable by voice — "Nabu, stop" / "Nabu, para") and two entities for dashboards: a ringing `binary_sensor` and a "Next Alarm" `sensor` listing every active alarm. See [Dashboard cards](#dashboard-cards) below for a ready-to-paste Lovelace example.

### Install (HACS custom repository)
1. HACS → Integrations → ⋮ → Custom repositories
2. URL: `https://github.com/rhythmcreative/voice-satellite-card-llm-tools`, category **Integration**
3. Install **Voice Satellite - LLM Tools+**, restart Home Assistant, then add it via Settings → Devices & Services and pick the **Alarms** tool type.

### Entities

| Entity | What it shows |
|---|---|
| `binary_sensor.<name>_alarm_ringing` | `on` while any alarm is ringing. Attributes: `alarm_label`, `alarm_time`, `alarm_sound_url`. |
| `sensor.<name>_next_alarm` | State = timestamp of the soonest scheduled alarm (or unavailable if none). Attributes: `alarms` (full list, each `{id, time, label, days, next_trigger}`), `count`. |

Exact entity IDs depend on how you named the config entry — check **Developer Tools → States** and filter for "alarm" to find yours.

### Dashboard cards

A ready-to-paste Lovelace example lives at [`dashboard/alarms_card.yaml`](dashboard/alarms_card.yaml) — shows a ringing banner with Stop/Snooze buttons, the list of active alarms, and a Test Alarm button. To use it:

1. Open your dashboard → ⋮ → **Edit Dashboard** → **+ Add Card** → scroll down → **Manual**.
2. Replace the entity IDs at the top of the YAML with your own (see the table above), paste the rest, and save.
3. Repeat for each card block if you're building it as separate cards instead of one stack.
