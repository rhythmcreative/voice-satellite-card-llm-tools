<h1 align="center" style="border-bottom: none">
<img alt="Voice Satellite - LLM Tools" src="https://raw.githubusercontent.com/rhythmcreative/voice-satellite-card-llm-tools/refs/heads/main/assets/banner.png" width="650" />
</h1>

<div align="center">

<p><i> Supercharge your Home Assistant Voice Satellite with Web Search, Wikipedia, Images, YouTube Videos, Weather Forecasts, Financial Data, Smart Lovelace Entity Cards, and Alexa-like Alarms powered by Wakey. </i></p>

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-41BDF5?style=for-the-badge&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://hacs.xyz/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Fork of jxlarrea](https://img.shields.io/badge/Fork%20of-jxlarrea%2Fvoice--satellite--card--llm--tools-blueviolet?style=for-the-badge&logo=github)](https://github.com/jxlarrea/voice-satellite-card-llm-tools)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

> [!NOTE]
> This repository is a maintained fork of [jxlarrea/voice-satellite-card-llm-tools](https://github.com/jxlarrea/voice-satellite-card-llm-tools) by [@jxlarrea](https://github.com/jxlarrea).
> 
> **Enhancements:**
> - **Full Alexa-like Voice Alarms** powered by [Wakey](https://github.com/rhythmcreative/wakey) (`set_alarm`, `list_alarms`, `cancel_alarm`, `snooze_alarm`, `stop_alarm`, `adjust_alarm`, `test_alarm`).
> - **Native Smart Display UI**: Redesigned borderless digital clock hero cards and list cards aligned with Voice Satellite's Google Nest Hub design language.
> - **Hands-Free Stop & Snooze**: Saying "stop" or "snooze" silences and dismisses any active ringing alarm without requiring an alarm ID.
> - **Multilingual Recurrence**: Supports natural English and Spanish day specifications (`weekdays`, `laborables`, `weekends`, `fines de semana`, `daily`).

______________________________________________________________________

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=ABOUT)](https://git.io/typing-svg)

Extend your voice assistant's capabilities with **web, Wikipedia, image, video search, weather forecast, financial data, and alarm tools** for Home Assistant's LLM integrations. When paired with the [Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration), results are displayed directly in the card UI.

When a conversation agent (OpenAI, Google Generative AI, Anthropic, Ollama, etc.) receives a request, it can call these tools to fetch results. The Voice Satellite renders the results visually on your smart displays and tablets.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rhythmcreative&repository=voice-satellite-card-llm-tools&category=integration)

______________________________________________________________________

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=VOICE+COMMANDS)](https://git.io/typing-svg)

- *"Set an alarm for 7:30 AM"*
- *"Wake me up at 8 with an alarm for gym"*
- *"Set an alarm for 6:30 AM every weekday"*
- *"What alarms do I have?"*
- *"Cancel my 7 AM alarm"*
- *"Stop the alarm"* / *"Snooze"*
- *"Change my 7 AM alarm to 7:30"*
- *"Search the web for best restaurants in Tokyo"*
- *"Tell me about Marie Curie"*
- *"Show me pictures of golden retrievers"*
- *"Search for videos on how to make sourdough bread"*
- *"What's the weather like tomorrow?"*
- *"What's the price of Apple stock?"*
- *"How much is Bitcoin right now?"*
- *"Show the living room camera"*

______________________________________________________________________

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=FEATURES)](https://git.io/typing-svg)

### Alarms (Wakey)

![Alarms](https://raw.githubusercontent.com/rhythmcreative/voice-satellite-card-llm-tools/refs/heads/main/assets/alarm.png)

Full voice alarm control powered by the [Wakey](https://github.com/rhythmcreative/wakey) integration:

- **Schedule alarms (`set_alarm`)**: One-time or recurring alarms with custom labels, target speaker, volume, and continuous looping. Supports English and Spanish days of the week (`weekdays`, `laborables`, `weekends`, `fines de semana`, `daily`). Duplicate alarm prevention included.
- **List alarms (`list_alarms`)**: Summarizes upcoming alarms and displays a clean, native card.
- **Cancel alarms (`cancel_alarm`)**: Cancel by alarm ID, time (*"cancel my 7 AM alarm"*), label (*"cancel medicine alarm"*), or cancel all at once.
- **Snooze & Stop (`snooze_alarm`, `stop_alarm`)**: Instantly snooze (default 9 minutes) or silence ringing alarms hands-free.
- **Adjust alarms (`adjust_alarm`)**: Shift the next occurrence to a new time without modifying the underlying schedule.
- **Test alarm (`test_alarm`)**: Preview the alarm audio on your speaker while showing the visual alarm screen.

---

### Weather Forecast

![Weather](https://github.com/user-attachments/assets/5c439e57-3047-4457-a18a-f8dbb778e1f7)

Get weather forecasts using your existing Home Assistant weather entities — no additional API key required. Supports today, tomorrow, specific days of the week, and weekly outlooks. Optionally include hour-by-hour detail, current temperature, and humidity readings from dedicated sensors.

---

### Financial Data

![Stocks](https://github.com/user-attachments/assets/20f66567-7e9c-4d69-af7d-cad699c6149e)

Look up stock prices, cryptocurrency prices, and convert currencies using [Finnhub](https://finnhub.io/). Stocks return current price, daily change, high/low, and company logo. Cryptocurrency queries (BTC, ETH, DOGE, and 25+ others) are automatically resolved via [CoinGecko](https://www.coingecko.com/). Currency conversion supports all major forex pairs.

---

### Entity Card

Show Home Assistant entities on the satellite screen. Ask to see a camera, a light, or a group of sensors and the assistant draws them as a real Lovelace card in the media panel while answering out loud. No API key required.

- Cameras render as picture cards using `camera_view: auto`, single or in a grid
- A single entity renders as a tile
- Several entities render as an entities list
- Trends or history render as a history graph

---

### Web Search
Search the web using [Brave Search API](https://brave.com/search/api/) or self-hosted [SearXNG](https://docs.searxng.org/). Returns page titles, snippets, and thumbnails.

### Wikipedia
Look up topics on Wikipedia — no API key required. Returns a single authoritative article with thumbnail. Choose between **Concise** (1-3 sentences) or **Detailed** (full intro).

### Image Search
Search for images using [Brave Search API](https://brave.com/search/api/) or [SearXNG](https://docs.searxng.org/). Supports SafeSearch and configurable result counts.

### Video Search
Search YouTube via the [YouTube Data API v3](https://developers.google.com/youtube/v3). Returns titles, thumbnails, channel names, durations, and view counts.

______________________________________________________________________

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=INSTALLATION)](https://git.io/typing-svg)

### Prerequisites

1. **[Voice Satellite](https://github.com/jxlarrea/voice-satellite-card-integration)** installed and configured.
2. A **conversation agent** with LLM tool support (OpenAI, Google Generative AI, Anthropic, Ollama, etc.).
3. **[Wakey](https://github.com/rhythmcreative/wakey)** installed (if using the Alarm tool).

### Via HACS (Recommended)

1. Open **HACS** → Click the three dots (⋮) in the top right → **Custom repositories**.
2. Add `https://github.com/rhythmcreative/voice-satellite-card-llm-tools` with category **Integration**.
3. Click **Download**, then restart Home Assistant.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rhythmcreative&repository=voice-satellite-card-llm-tools&category=integration)

### Manual Installation

1. Download the [latest release](https://github.com/rhythmcreative/voice-satellite-card-llm-tools/releases/latest).
2. Copy `custom_components/voice_satellite_llm_tools` to your `config/custom_components/` directory.
3. Restart Home Assistant.

______________________________________________________________________

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=SETUP+%26+OPTIONS)](https://git.io/typing-svg)

Each tool is configured as a separate entry via **Settings > Devices & Services > Add Integration > Voice Satellite LLM Tools**.

After adding a tool, enable its LLM API in your assistant pipeline: Go to **Settings > Voice Assistants**, select your pipeline, click the gear icon next to **Conversation Agent**, and enable the tools under **Tool Providers** or **Control Home Assistant**.

| Tool | Setup Steps |
|------|-------------|
| **Alarms (Wakey)** | Select default media player, sound URI, volume, looping (0 = continuous), and snooze |
| **Web Search** | Select provider (Brave/SearXNG) → enter credentials → configure max results |
| **Wikipedia** | Choose detail level (Concise/Detailed) |
| **Image Search** | Select provider (Brave/SearXNG) → enter credentials → configure max results |
| **Video Search** | Enter YouTube Data API v3 key → configure max results |
| **Weather Forecast** | Select daily weather entity → optionally add hourly entity, temperature, and humidity sensors |
| **Financial Data** | Select provider (Finnhub) → enter API key |
| **Entity Card** | Set max entities per card and the history range |

### Configuration Options Reference

| Tool | Option | Description |
|------|--------|-------------|
| **Alarms (Wakey)** | Default Media Player | Speaker or media player where alarms will sound |
| | Default Sound URI | URI of alarm audio file (e.g. `media-source://media_source/local/alarms/alarm_oxygen_gentle.mp3`) |
| | Default Volume | 0.0 - 1.0 (default: 0.7) |
| | Repeat Count | 0 - 100 (default: 0 = continuous loop until stopped or snoozed) |
| | Snooze Minutes | 1 - 120 minutes (default: 9) |
| **Web Search** | Provider | Brave or SearXNG |
| | API Key / URL | Credentials for your chosen search provider |
| | Max Results | 1-6 (default: 3) |
| **Wikipedia** | Article Detail | Concise (short summary) or Detailed (full intro) |
| **Image Search** | Provider | Brave or SearXNG |
| | SafeSearch | off, moderate, or strict (Brave) |
| | Max Results | 1-10 (default: 3) |
| **Video Search** | YouTube API Key | Google Cloud YouTube Data API v3 key |
| | Max Results | 1-6 (default: 3) |
| **Weather Forecast** | Daily Forecast Entity | Primary weather entity (required) |
| | Hourly / Sensors | Optional sensors for detailed forecasts and current conditions |
| **Financial Data** | Finnhub API Key | Free API key from [finnhub.io](https://finnhub.io/) |
| **Entity Card** | Maximum Entities | 1-12 (default: 6) |
| | History Range | 1-168 hours (default: 24) |

______________________________________________________________________

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=CREDITS+%26+LICENSE)](https://git.io/typing-svg)

- **Original Creator:** Developed by [@jxlarrea](https://github.com/jxlarrea) in [voice-satellite-card-llm-tools](https://github.com/jxlarrea/voice-satellite-card-llm-tools).
- **Alarm Integration:** Powered by [Wakey](https://github.com/rhythmcreative/wakey).
- **License:** MIT License. See [LICENSE](LICENSE) for details.
