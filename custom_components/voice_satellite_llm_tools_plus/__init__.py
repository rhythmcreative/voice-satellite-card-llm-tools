"""The Voice Satellite LLM Tools integration."""

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ADDON_NAME,
    ALARM_SOUNDS_PATH,
    CONF_TOOL_TYPE,
    DOMAIN,
    TOOL_TYPE_ALARM,
    WEATHER_ICONS_PATH,
)
from .llm_api import cleanup_llm_api, setup_llm_api

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_TEST_ALARM = "test_alarm"
SERVICE_STOP_ALARM = "stop_alarm"
SERVICE_SNOOZE_ALARM = "snooze_alarm"

ALARM_PLATFORMS = ["binary_sensor", "sensor"]


def _find_alarm_manager(hass: HomeAssistant):
    """Return the AlarmManager for the (single) configured Alarms entry, if any."""
    for entry_data in hass.data.get(DOMAIN, {}).get("entries", {}).values():
        manager = entry_data.get("alarm_manager")
        if manager is not None:
            return manager
    return None


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Voice Satellite LLM Tools integration."""
    hass.data.setdefault(DOMAIN, {"cache": {}, "entries": {}})

    icons_dir = str(Path(__file__).parent / "weather_icons")
    sounds_dir = str(Path(__file__).parent / "alarm_sounds")
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(WEATHER_ICONS_PATH, icons_dir, cache_headers=True),
            StaticPathConfig(ALARM_SOUNDS_PATH, sounds_dir, cache_headers=True),
        ]
    )

    async def _async_handle_test_alarm(call: ServiceCall) -> None:
        """Ring the configured Alarms tool once, immediately, for testing."""
        manager = _find_alarm_manager(hass)
        if manager is None:
            _LOGGER.warning("No Alarms tool is configured; nothing to test")
            return
        result = await manager.async_test_ring()
        if not result["ok"]:
            _LOGGER.error("Alarm test failed: %s", result["error"])

    async def _async_handle_stop_alarm(call: ServiceCall) -> None:
        """Stop whichever alarm is currently ringing, independent of any LLM."""
        manager = _find_alarm_manager(hass)
        if manager is None:
            _LOGGER.warning("No Alarms tool is configured; nothing to stop")
            return
        await manager.async_stop_ringing()

    async def _async_handle_snooze_alarm(call: ServiceCall) -> None:
        """Snooze whichever alarm is currently ringing, independent of any LLM."""
        manager = _find_alarm_manager(hass)
        if manager is None:
            _LOGGER.warning("No Alarms tool is configured; nothing to snooze")
            return
        minutes = call.data.get("minutes", 9)
        await manager.async_snooze(minutes)

    hass.services.async_register(DOMAIN, SERVICE_TEST_ALARM, _async_handle_test_alarm)
    hass.services.async_register(DOMAIN, SERVICE_STOP_ALARM, _async_handle_stop_alarm)
    hass.services.async_register(DOMAIN, SERVICE_SNOOZE_ALARM, _async_handle_snooze_alarm)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Voice Satellite LLM Tools from a config entry."""
    _LOGGER.info("Setting up %s for entry: %s", ADDON_NAME, entry.entry_id)
    config = {**entry.data, **(entry.options or {})}
    await setup_llm_api(hass, config, entry.entry_id)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    if config.get(CONF_TOOL_TYPE) == TOOL_TYPE_ALARM:
        await hass.config_entries.async_forward_entry_setups(entry, ALARM_PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading %s for entry: %s", ADDON_NAME, entry.entry_id)
    config = {**entry.data, **(entry.options or {})}
    unload_ok = True
    if config.get(CONF_TOOL_TYPE) == TOOL_TYPE_ALARM:
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry, ALARM_PLATFORMS
        )
    await cleanup_llm_api(hass, entry.entry_id)
    return unload_ok
