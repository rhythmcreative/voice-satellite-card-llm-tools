"""Constants for the Voice Satellite LLM Tools integration."""

DOMAIN = "voice_satellite_llm_tools_plus"
ADDON_NAME = "Voice Satellite LLM Tools+"
WEATHER_ICONS_PATH = f"/api/{DOMAIN}/weather_icons"
ALARM_SOUNDS_PATH = f"/api/{DOMAIN}/alarm_sounds"

# Tool type selection
CONF_TOOL_TYPE = "tool_type"
TOOL_TYPE_IMAGE_SEARCH = "image_search"
TOOL_TYPE_VIDEO_SEARCH = "video_search"
TOOL_TYPE_WEB_SEARCH = "web_search"
TOOL_TYPE_WIKIPEDIA = "wikipedia"
TOOL_TYPE_WEATHER = "weather"
TOOL_TYPE_FINANCIAL = "financial_data"
TOOL_TYPE_ALARM = "alarm"

CONF_TOOL_TYPES = {
    TOOL_TYPE_IMAGE_SEARCH: "Image Search",
    TOOL_TYPE_VIDEO_SEARCH: "Video Search",
    TOOL_TYPE_WEB_SEARCH: "Web Search",
    TOOL_TYPE_WIKIPEDIA: "Wikipedia",
    TOOL_TYPE_WEATHER: "Weather Forecast",
    TOOL_TYPE_FINANCIAL: "Financial Data",
    TOOL_TYPE_ALARM: "Alarms",
}

# LLM API identifiers
IMAGE_SEARCH_API_NAME = "Voice Satellite: Image Search"
IMAGE_SEARCH_API_ID = "voice_satellite_llm_tools_image_search"

IMAGE_SEARCH_SERVICES_PROMPT = (
    "You may use the Image Search Services tools to find images on the internet. "
    "When the user asks you to find, search for, or show images, use the search_images tool. "
    "Set auto_display to true when the user wants to see a specific image immediately "
    "(e.g. 'show me the Mona Lisa', 'what does a pangolin look like'). "
    "Set auto_display to false when they want to browse multiple results "
    "(e.g. 'find me pictures of cats', 'search for sunset photos')."
)

# Video Search LLM API identifiers
VIDEO_SEARCH_API_NAME = "Voice Satellite: Video Search"
VIDEO_SEARCH_API_ID = "voice_satellite_llm_tools_video_search"

VIDEO_SEARCH_SERVICES_PROMPT = (
    "You may use the Video Search Services tools to find videos on YouTube. "
    "When the user asks you to find, search for, or show videos, use the search_videos tool. "
    "Set auto_play to true when the user wants to watch a specific video immediately "
    "(e.g. 'play the latest MrBeast video', 'show me that rickroll video'). "
    "Set auto_play to false when they want to browse or explore results "
    "(e.g. 'find me videos about cooking', 'search for guitar tutorials')."
)

# Web Search LLM API identifiers
WEB_SEARCH_API_NAME = "Voice Satellite: Web Search"
WEB_SEARCH_API_ID = "voice_satellite_llm_tools_web_search"

WEB_SEARCH_SERVICES_PROMPT = (
    "You may use the Web Search tool to search the internet for information. "
    "When the user asks a question that requires current information, facts, or general knowledge "
    "that you are not sure about, use the search_web tool."
)

# Wikipedia Search LLM API identifiers
WIKIPEDIA_API_NAME = "Voice Satellite: Wikipedia"
WIKIPEDIA_API_ID = "voice_satellite_llm_tools_wikipedia"

WIKIPEDIA_SERVICES_PROMPT = (
    "You may use the Wikipedia Search tool to look up encyclopedic information. "
    "When the user asks about a topic, person, place, event, or concept that Wikipedia would cover, "
    "use the search_wikipedia tool."
)

# Weather Forecast LLM API identifiers
WEATHER_API_NAME = "Voice Satellite: Weather Forecast"
WEATHER_API_ID = "voice_satellite_llm_tools_weather"

WEATHER_SERVICES_PROMPT = (
    "You may use the Weather Forecast tool to get weather information. "
    "When the user asks about the weather, temperature, or forecast for today, "
    "tomorrow, a specific day of the week, or the upcoming week, use the "
    "get_weather_forecast tool with the appropriate range parameter."
)

# Provider selection
CONF_IMAGE_SEARCH_PROVIDER = "image_search_provider"
CONF_IMAGE_SEARCH_PROVIDER_BRAVE = "Brave"
CONF_IMAGE_SEARCH_PROVIDER_SEARXNG = "SearXNG"

CONF_IMAGE_SEARCH_PROVIDERS = {
    "Brave": CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    "SearXNG": CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
}

# Brave Image Search config keys
CONF_BRAVE_API_KEY = "brave_api_key"
CONF_BRAVE_IMAGE_NUM_RESULTS = "brave_image_num_results"
CONF_BRAVE_SAFESEARCH = "brave_safesearch"

# SearXNG config keys
CONF_SEARXNG_URL = "searxng_server_url"
CONF_SEARXNG_IMAGE_NUM_RESULTS = "searxng_image_num_results"
CONF_SEARXNG_ENGINES = "searxng_engines"

# Web Search provider selection
CONF_WEB_SEARCH_PROVIDER = "web_search_provider"
CONF_WEB_SEARCH_PROVIDER_BRAVE = "Brave"
CONF_WEB_SEARCH_PROVIDER_SEARXNG = "SearXNG"

CONF_WEB_SEARCH_PROVIDERS = {
    "Brave": CONF_WEB_SEARCH_PROVIDER_BRAVE,
    "SearXNG": CONF_WEB_SEARCH_PROVIDER_SEARXNG,
}

# Brave Web Search config keys
CONF_BRAVE_WEB_NUM_RESULTS = "brave_web_num_results"

# SearXNG Web Search config keys
CONF_SEARXNG_WEB_NUM_RESULTS = "searxng_web_num_results"
CONF_SEARXNG_WEB_ENGINES = "searxng_web_engines"

# Wikipedia config keys
CONF_WIKIPEDIA_DETAIL = "wikipedia_detail"
WIKIPEDIA_DETAIL_CONCISE = "concise"
WIKIPEDIA_DETAIL_DETAILED = "detailed"

CONF_WIKIPEDIA_DETAIL_OPTIONS = {
    WIKIPEDIA_DETAIL_CONCISE: "Concise",
    WIKIPEDIA_DETAIL_DETAILED: "Detailed",
}

# Financial Data LLM API identifiers
FINANCIAL_API_NAME = "Voice Satellite: Financial Data"
FINANCIAL_API_ID = "voice_satellite_llm_tools_financial"

FINANCIAL_SERVICES_PROMPT = (
    "You may use the Financial Data tool to look up stock prices, cryptocurrency prices, "
    "and convert currencies. "
    "When the user asks about a stock price, cryptocurrency price, market data, "
    "or how a stock or crypto is doing, use the get_financial_data tool with "
    "query_type 'stock' and the ticker symbol (e.g. AAPL, TSLA, BTC, ETH). "
    "When the user asks to convert currencies or about exchange rates, "
    "use the get_financial_data tool with query_type 'currency'."
)

# Financial Data provider selection
CONF_FINANCIAL_PROVIDER = "financial_provider"
CONF_FINANCIAL_PROVIDER_FINNHUB = "Finnhub"

CONF_FINANCIAL_PROVIDERS = {
    "Finnhub": CONF_FINANCIAL_PROVIDER_FINNHUB,
}

# Finnhub config keys
CONF_FINNHUB_API_KEY = "finnhub_api_key"

# Financial Data defaults
FINANCIAL_DEFAULTS = {
    CONF_FINNHUB_API_KEY: "",
}

# Weather Forecast config keys
CONF_DAILY_WEATHER_ENTITY = "daily_weather_entity"
CONF_HOURLY_WEATHER_ENTITY = "hourly_weather_entity"
CONF_WEATHER_TEMPERATURE_SENSOR = "weather_temperature_sensor"
CONF_WEATHER_HUMIDITY_SENSOR = "weather_humidity_sensor"

# YouTube Data API v3 config keys
CONF_YOUTUBE_API_KEY = "youtube_api_key"
CONF_YOUTUBE_NUM_RESULTS = "youtube_num_results"

# Cache config
CONF_CACHE_TTL = "cache_ttl"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Image search defaults
IMAGE_SEARCH_DEFAULTS = {
    CONF_BRAVE_API_KEY: "",
    CONF_BRAVE_IMAGE_NUM_RESULTS: 3,
    CONF_BRAVE_SAFESEARCH: "moderate",
    CONF_SEARXNG_URL: "",
    CONF_SEARXNG_IMAGE_NUM_RESULTS: 3,
    CONF_SEARXNG_ENGINES: "",
}

# Web search defaults
WEB_SEARCH_DEFAULTS = {
    CONF_BRAVE_API_KEY: "",
    CONF_BRAVE_WEB_NUM_RESULTS: 3,
    CONF_SEARXNG_URL: "",
    CONF_SEARXNG_WEB_NUM_RESULTS: 3,
    CONF_SEARXNG_WEB_ENGINES: "",
}

# Wikipedia defaults
WIKIPEDIA_DEFAULTS = {
    CONF_WIKIPEDIA_DETAIL: WIKIPEDIA_DETAIL_CONCISE,
}

# Video search defaults
VIDEO_SEARCH_DEFAULTS = {
    CONF_YOUTUBE_API_KEY: "",
    CONF_YOUTUBE_NUM_RESULTS: 3,
}

# Alarm LLM API identifiers
ALARM_API_NAME = "Voice Satellite: Alarms"
ALARM_API_ID = "voice_satellite_llm_tools_alarms"

ALARM_SERVICES_PROMPT = (
    "You may use the Alarm tools to manage voice-announced alarms. This "
    "assistant is used in both English and Spanish — treat both languages "
    "as equally valid triggers for every tool below. "
    "Use set_alarm when the user asks to set, schedule, or create an alarm "
    "(e.g. 'set an alarm for 7:30', 'wake me up at 6am every weekday', "
    "'ponme una alarma a las 7:30', 'despiértame a las 6 entre semana'). "
    "Use list_alarms when they ask what alarms are currently set (e.g. "
    "'what alarms do I have', 'qué alarmas tengo'). "
    "Use cancel_alarm when they ask to delete or remove a specific alarm, or "
    "all alarms at once (e.g. 'cancel my alarm', 'borra la alarma'). "
    "Use test_alarm when the user asks to test, try, or preview what the "
    "alarm sounds like (e.g. 'test the alarm', 'prueba la alarma'). "
    "ALWAYS call stop_alarm — immediately, with no confirmation question, "
    "and even if you are not fully sure an alarm is ringing — whenever the "
    "user's message is a short, bare imperative that could mean stop/silence "
    "a sound. This includes, in English: 'stop', 'stop it', 'silence', "
    "'turn it off', 'shut up', 'quiet', 'enough', 'Nabu stop'. And in "
    "Spanish: 'para', 'ya para', 'basta', 'cállate', 'silencio', 'apágala', "
    "'quítala', 'Nabu para'. Prefer calling stop_alarm over replying "
    "conversationally whenever a message this short and imperative could "
    "plausibly be about a ringing alarm — calling it when nothing is "
    "ringing is harmless and returns a normal 'nothing is ringing' result."
)

# Alarm config keys
# alarm_satellite_entity accepts either an assist_satellite entity (rung via
# assist_satellite.announce) or a media_player entity (rung via media_player.play_media,
# sound only) — the target's domain decides which.
CONF_ALARM_SATELLITE_ENTITY = "alarm_satellite_entity"
CONF_ALARM_SOUND = "alarm_sound"
CONF_ALARM_SOUND_URL = "alarm_sound_url"
CONF_ALARM_RING_COUNT = "alarm_ring_count"
CONF_ALARM_RING_INTERVAL_SECONDS = "alarm_ring_interval_seconds"

# Fallback spacing between re-announcements when not configured by the user.
ALARM_RING_INTERVAL_SECONDS = 20

# Safety cap on how many times an alarm re-rings before auto-stopping, so a
# missed alarm can't ring forever. 45 * 20s ≈ 15 minutes. A real alarm rings
# until the user stops or snoozes it; this only bounds the worst case.
ALARM_MAX_RINGS = 45

# Dispatcher signal (format with entry_id) broadcast whenever an entry's
# ringing state changes, so the binary_sensor entity can update live.
SIGNAL_ALARM_RINGING = f"{DOMAIN}_alarm_ringing_{{}}"

# Dispatcher signal (format with entry_id) broadcast whenever an entry's
# alarm list changes (set/cancel/snooze/reschedule), so the Next Alarm
# sensor can refresh its state and attributes live.
SIGNAL_ALARMS_UPDATED = f"{DOMAIN}_alarms_updated_{{}}"

# Built-in alarm sounds, bundled with the integration and served as static files.
# Values are paths relative to the Home Assistant base URL.
ALARM_SOUND_NONE = "none"
BUILTIN_ALARM_SOUNDS = {
    ALARM_SOUND_NONE: "",
    "classic_alarm": f"{ALARM_SOUNDS_PATH}/classic_alarm.mp3",
    "beep": f"{ALARM_SOUNDS_PATH}/beep.wav",
    "double_beep": f"{ALARM_SOUNDS_PATH}/double_beep.wav",
    "siren": f"{ALARM_SOUNDS_PATH}/siren.wav",
}

CONF_ALARM_SOUND_OPTIONS = {
    ALARM_SOUND_NONE: "None (spoken announcement only)",
    "classic_alarm": "Classic Alarm Clock",
    "beep": "Beep",
    "double_beep": "Double Beep",
    "siren": "Siren",
}

# Alarm defaults
ALARM_DEFAULTS = {
    CONF_ALARM_SOUND: "classic_alarm",
    CONF_ALARM_SOUND_URL: "",
    CONF_ALARM_RING_COUNT: 3,
    CONF_ALARM_RING_INTERVAL_SECONDS: ALARM_RING_INTERVAL_SECONDS,
}
