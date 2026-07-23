"""Binary sensor reporting whether an alarm is currently ringing."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ADDON_NAME, DOMAIN, SIGNAL_ALARM_RINGING

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the alarm-ringing binary sensor for this entry."""
    entry_data = hass.data.get(DOMAIN, {}).get("entries", {}).get(entry.entry_id)
    manager = entry_data.get("alarm_manager") if entry_data else None
    if manager is None:
        _LOGGER.debug("No AlarmManager for entry %s; skipping binary_sensor", entry.entry_id)
        return

    async_add_entities([AlarmRingingBinarySensor(manager, entry)])


class AlarmRingingBinarySensor(BinarySensorEntity):
    """Reflects whether any alarm managed by this entry is ringing right now."""

    _attr_device_class = BinarySensorDeviceClass.SOUND
    _attr_icon = "mdi:alarm-light"
    _attr_should_poll = False

    def __init__(self, manager, entry: ConfigEntry) -> None:
        """Initialize the sensor from the entry's AlarmManager."""
        self._manager = manager
        self._attr_unique_id = f"{entry.entry_id}_alarm_ringing"
        self._attr_is_on = manager.is_ringing()
        self._attr_name = f"{ADDON_NAME} Alarm Ringing"

    @property
    def extra_state_attributes(self) -> dict:
        """Expose the ringing alarm's label and set time for the card overlay."""
        try:
            return self._manager.ringing_info()
        except Exception:  # noqa: BLE001 - attributes must never raise
            return {}

    async def async_added_to_hass(self) -> None:
        """Subscribe to ringing-state changes from the AlarmManager."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_ALARM_RINGING.format(self._manager.entry_id),
                self._handle_ringing_update,
            )
        )

    @callback
    def _handle_ringing_update(self, is_ringing: bool) -> None:
        """Update state when the AlarmManager reports a ringing-state change."""
        self._attr_is_on = is_ringing
        self.async_write_ha_state()
