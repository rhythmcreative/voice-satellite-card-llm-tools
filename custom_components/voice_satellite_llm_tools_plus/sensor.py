"""Sensor exposing the soonest scheduled alarm and the full active-alarm list."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import ADDON_NAME, DOMAIN, SIGNAL_ALARMS_UPDATED

_LOGGER = logging.getLogger(__name__)

_WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the next-alarm sensor for this entry."""
    entry_data = hass.data.get(DOMAIN, {}).get("entries", {}).get(entry.entry_id)
    manager = entry_data.get("alarm_manager") if entry_data else None
    if manager is None:
        _LOGGER.debug("No AlarmManager for entry %s; skipping sensor", entry.entry_id)
        return

    async_add_entities([NextAlarmSensor(manager, entry)])


class NextAlarmSensor(SensorEntity):
    """Reports the soonest scheduled alarm's time and lists every active alarm.

    Built for Lovelace dashboard cards (markdown / template) that want to
    show "active alarms" at a glance: the `alarms` attribute is a list of
    {id, time, label, days, next_trigger} dicts, sorted by trigger time.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:alarm-multiple"
    _attr_should_poll = False

    def __init__(self, manager, entry: ConfigEntry) -> None:
        """Initialize from the entry's AlarmManager and compute the initial state."""
        self._manager = manager
        self._attr_unique_id = f"{entry.entry_id}_next_alarm"
        self._attr_name = f"{ADDON_NAME} Next Alarm"
        self._refresh()

    async def async_added_to_hass(self) -> None:
        """Subscribe to alarm-list changes from the AlarmManager."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_ALARMS_UPDATED.format(self._manager.entry_id),
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Refresh state and attributes when alarms are set/cancelled/rescheduled."""
        self._refresh()
        self.async_write_ha_state()

    def _refresh(self) -> None:
        """Recompute native value and attributes from the manager's current alarms."""
        try:
            alarms = self._manager.async_list_alarms()
        except Exception:  # noqa: BLE001 - state must never raise
            alarms = []

        items = []
        for a in alarms:
            days = a.get("days")
            items.append({
                "id": a["id"],
                "time": f"{a['hour']:02d}:{a['minute']:02d}",
                "label": a.get("label", ""),
                "days": [_WEEKDAY_NAMES[d] for d in days] if days else [],
                "next_trigger": a["next_trigger"],
            })

        self._attr_native_value = (
            dt_util.parse_datetime(alarms[0]["next_trigger"]) if alarms else None
        )
        self._attr_extra_state_attributes = {"alarms": items, "count": len(items)}
