"""The Voice Satellite LLM Tools integration."""

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import (
    ADDON_NAME,
    ALARM_CARD_FILENAME,
    ALARM_CARD_URL,
    DOMAIN,
    FRONTEND_PATH,
    VERSION,
    WEATHER_ICONS_PATH,
)
from .llm_api import cleanup_llm_api, setup_llm_api

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Register frontend Lovelace resource for the alarm card."""
    frontend_dir = str(Path(__file__).parent / "frontend")
    card_path = str(Path(frontend_dir) / ALARM_CARD_FILENAME)

    if not Path(card_path).exists():
        _LOGGER.debug("Alarm card frontend not found at %s", card_path)
        return

    try:
        cache_bust = int(Path(card_path).stat().st_mtime)
    except OSError:
        cache_bust = 0

    versioned_url = f"{ALARM_CARD_URL}?v={VERSION}&m={cache_bust}"

    # Register static path
    if not hass.data.get(f"{DOMAIN}_frontend_registered"):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(FRONTEND_PATH, frontend_dir, cache_headers=False)]
        )
        hass.data[f"{DOMAIN}_frontend_registered"] = True

    # Register via add_extra_js_url
    add_extra_js_url(hass, versioned_url)

    # Register in Lovelace storage resources if available
    lovelace = hass.data.get("lovelace")
    resources = (
        lovelace.resources
        if hasattr(lovelace, "resources")
        else lovelace.get("resources") if isinstance(lovelace, dict) else None
    )
    if resources and hasattr(resources, "async_create_item"):
        try:
            if hasattr(resources, "async_get_info"):
                await resources.async_get_info()
            items = resources.async_items() if hasattr(resources, "async_items") else []
            exists = any(ALARM_CARD_FILENAME in (item.get("url") or "") for item in items)
            if not exists:
                await resources.async_create_item(
                    {"res_type": "module", "url": versioned_url}
                )
                _LOGGER.debug("Registered alarm card in Lovelace resources: %s", versioned_url)
        except Exception as err:
            _LOGGER.debug("Could not register in Lovelace storage resources: %s", err)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Voice Satellite LLM Tools integration."""
    hass.data.setdefault(DOMAIN, {"cache": {}, "entries": {}})

    icons_dir = str(Path(__file__).parent / "weather_icons")
    await hass.http.async_register_static_paths(
        [StaticPathConfig(WEATHER_ICONS_PATH, icons_dir, cache_headers=True)]
    )

    await _async_register_frontend(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Voice Satellite LLM Tools from a config entry."""
    _LOGGER.info("Setting up %s for entry: %s", ADDON_NAME, entry.entry_id)
    config = {**entry.data, **(entry.options or {})}
    await setup_llm_api(hass, config, entry.entry_id)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading %s for entry: %s", ADDON_NAME, entry.entry_id)
    await cleanup_llm_api(hass, entry.entry_id)
    return True
