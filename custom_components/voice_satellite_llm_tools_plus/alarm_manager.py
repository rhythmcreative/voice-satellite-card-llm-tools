"""Schedules, rings, and cancels voice-announced alarms for one config entry."""

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_point_in_time
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ALARM_MAX_RINGS,
    ALARM_RING_INTERVAL_SECONDS,
    ALARM_SOUND_NONE,
    BUILTIN_ALARM_SOUNDS,
    CONF_ALARM_RING_COUNT,
    CONF_ALARM_RING_INTERVAL_SECONDS,
    CONF_ALARM_SATELLITE_ENTITY,
    CONF_ALARM_SOUND,
    CONF_ALARM_SOUND_URL,
    DOMAIN,
    SIGNAL_ALARM_RINGING,
    SIGNAL_ALARMS_UPDATED,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1


class AlarmManager:
    """Owns the scheduling, ringing, and persistence of alarms for one entry."""

    def __init__(self, hass: HomeAssistant, config: dict, entry_id: str) -> None:
        """Initialize the manager for a given config entry."""
        self.hass = hass
        self.config = config
        self.entry_id = entry_id
        self._store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}_alarms_{entry_id}")
        self._alarms: dict[str, dict] = {}
        self._next_id = 1
        self._unsub_schedule: dict[str, callable] = {}
        self._ringing: dict[str, dict] = {}

    async def async_load(self) -> None:
        """Load persisted alarms and reschedule the pending ones."""
        data = await self._store.async_load()
        if data:
            self._alarms = data.get("alarms", {})
            self._next_id = data.get("next_id", 1)
        for alarm_id, alarm in list(self._alarms.items()):
            self._schedule(alarm_id, alarm)

    async def _async_save(self) -> None:
        """Persist current alarms to storage."""
        await self._store.async_save({"alarms": self._alarms, "next_id": self._next_id})

    @staticmethod
    def _resolve_next_trigger(
        hour: int, minute: int, days: list[int] | None
    ) -> datetime:
        """Resolve the next datetime a given hour:minute (optionally on given weekdays) occurs."""
        now = dt_util.now()
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if not days:
            if candidate <= now:
                candidate += timedelta(days=1)
            return candidate

        for offset in range(8):
            check = candidate + timedelta(days=offset)
            if check.weekday() in days and check > now:
                return check
        return candidate + timedelta(days=1)

    def _schedule(self, alarm_id: str, alarm: dict) -> None:
        """(Re)schedule the point-in-time callback that fires an alarm."""
        self._unschedule(alarm_id)

        next_trigger = dt_util.parse_datetime(alarm["next_trigger"])
        if next_trigger is None or next_trigger <= dt_util.now():
            next_trigger = self._resolve_next_trigger(
                alarm["hour"], alarm["minute"], alarm.get("days")
            )
            alarm["next_trigger"] = next_trigger.isoformat()

        async def _fire(_now, alarm_id=alarm_id) -> None:
            await self._async_ring(alarm_id)

        self._unsub_schedule[alarm_id] = async_track_point_in_time(
            self.hass, _fire, next_trigger
        )

    def _unschedule(self, alarm_id: str) -> None:
        """Cancel the pending point-in-time callback for an alarm, if any."""
        unsub = self._unsub_schedule.pop(alarm_id, None)
        if unsub:
            unsub()

    async def async_set_alarm(
        self, hour: int, minute: int, label: str = "", days: list[int] | None = None
    ) -> dict:
        """Create, schedule, and persist a new alarm. Returns the created record."""
        alarm_id = str(self._next_id)
        self._next_id += 1

        next_trigger = self._resolve_next_trigger(hour, minute, days)
        alarm = {
            "id": alarm_id,
            "hour": hour,
            "minute": minute,
            "label": label,
            "days": days,
            "next_trigger": next_trigger.isoformat(),
        }
        self._alarms[alarm_id] = alarm
        self._schedule(alarm_id, alarm)
        await self._async_save()
        self._notify_alarms_updated()
        return alarm

    async def async_cancel_alarm(self, alarm_id: str) -> bool:
        """Cancel a specific alarm, or every alarm if alarm_id == 'all'."""
        if alarm_id == "all":
            for aid in list(self._alarms):
                self._unschedule(aid)
                self._stop_ringing(aid)
            self._alarms.clear()
            await self._async_save()
            self._notify_alarms_updated()
            return True

        if alarm_id not in self._alarms:
            return False

        self._unschedule(alarm_id)
        self._stop_ringing(alarm_id)
        del self._alarms[alarm_id]
        await self._async_save()
        self._notify_alarms_updated()
        return True

    def async_list_alarms(self) -> list[dict]:
        """Return all scheduled alarms sorted by their next trigger time."""
        return sorted(self._alarms.values(), key=lambda a: a["next_trigger"])

    def is_ringing(self) -> bool:
        """Return whether any alarm is currently ringing."""
        return bool(self._ringing)

    def ringing_info(self) -> dict:
        """Return {label, time} for the currently ringing alarm, if any.

        Exposed on the alarm-ringing binary_sensor so the Voice Satellite
        card's visual overlay can label the alarm and show its set time.
        """
        for state in self._ringing.values():
            return {
                "alarm_label": state.get("label", ""),
                "alarm_time": state.get("time", ""),
                "alarm_sound_url": self._resolve_sound_url() or "",
            }
        return {"alarm_label": "", "alarm_time": "", "alarm_sound_url": ""}

    def _notify_ringing_state(self) -> None:
        """Broadcast the current ringing state to the binary_sensor entity."""
        async_dispatcher_send(
            self.hass, SIGNAL_ALARM_RINGING.format(self.entry_id), self.is_ringing()
        )

    def _notify_alarms_updated(self) -> None:
        """Broadcast that the alarm list changed, so the Next Alarm sensor refreshes."""
        async_dispatcher_send(self.hass, SIGNAL_ALARMS_UPDATED.format(self.entry_id))

    async def async_stop_ringing(self) -> bool:
        """Stop whichever alarm(s) are currently ringing (the 'Nabu, stop' path)."""
        if not self._ringing:
            return False
        for alarm_id in list(self._ringing):
            self._stop_ringing(alarm_id)
        await self._async_send_alarm_clear()
        return True

    async def async_snooze(self, minutes: int = 9) -> bool:
        """Snooze the currently ringing alarm(s): silence now, re-ring in N minutes.

        Called by the Voice Satellite card's alarm-overlay Snooze button
        (via the snooze_alarm service). Each ringing alarm is stopped and a
        one-shot snooze alarm is scheduled `minutes` from now, preserving the
        original label. Returns False when nothing is ringing.
        """
        if not self._ringing:
            return False

        try:
            minutes = int(minutes)
        except (TypeError, ValueError):
            minutes = 9
        minutes = max(1, min(60, minutes))

        ring_ids = list(self._ringing)
        labels = {}
        for alarm_id in ring_ids:
            base = self._alarms.get(alarm_id)
            labels[alarm_id] = base.get("label", "") if base else ""
            self._stop_ringing(alarm_id)
        await self._async_send_alarm_clear()

        when = dt_util.now() + timedelta(minutes=minutes)
        for alarm_id in ring_ids:
            snooze_id = str(self._next_id)
            self._next_id += 1
            snooze_alarm = {
                "id": snooze_id,
                "hour": when.hour,
                "minute": when.minute,
                "label": labels[alarm_id],
                "days": None,
                "next_trigger": when.isoformat(),
            }
            self._alarms[snooze_id] = snooze_alarm
            self._schedule(snooze_id, snooze_alarm)

        await self._async_save()
        self._notify_alarms_updated()
        _LOGGER.debug("Snoozed %d alarm(s) for %d minute(s)", len(ring_ids), minutes)
        return True

    async def _async_send_alarm_clear(self) -> None:
        """Tell the Voice Satellite card (if present) to clear its alarm alert."""
        target_entity = self.config.get(CONF_ALARM_SATELLITE_ENTITY)
        if not target_entity:
            return
        if target_entity.split(".", 1)[0] != "assist_satellite":
            return
        if not self._has_voice_satellite_card():
            return
        try:
            await self.hass.services.async_call(
                "assist_satellite",
                "announce",
                {"entity_id": target_entity, "message": "ALARM_CLEAR"},
                blocking=False,
            )
        except Exception as e:
            _LOGGER.debug("Failed to send alarm-clear signal to %s: %s", target_entity, e)

    def _stop_ringing(self, alarm_id: str) -> None:
        """Mark an in-progress ring as stopped and cancel its pending timer."""
        state = self._ringing.pop(alarm_id, None)
        if not state:
            return
        state["stopped"] = True
        unsub = state.get("repeat_unsub")
        if unsub:
            unsub()
        self._notify_ringing_state()

    async def _async_ring(self, alarm_id: str) -> None:
        """Fire an alarm: announce it up to CONF_ALARM_RING_COUNT times, then stop."""
        alarm = self._alarms.get(alarm_id)
        if alarm is None:
            return

        state = {
            "stopped": False,
            "repeat_unsub": None,
            "rings_done": 0,
            "label": alarm.get("label", ""),
            "time": f"{alarm.get('hour', 0):02d}:{alarm.get('minute', 0):02d}",
        }
        self._ringing[alarm_id] = state
        self._notify_ringing_state()

        # Re-announces up to the configured ring count, spaced by the
        # configured interval, then stops on its own if nobody said stop.
        # ALARM_MAX_RINGS is only a defensive ceiling (the UI caps ring
        # count at 10, well under it) in case a higher value is set via
        # YAML/automation.
        try:
            ring_count = int(self.config.get(CONF_ALARM_RING_COUNT, 3) or 3)
        except (TypeError, ValueError):
            ring_count = 3
        max_rings = max(1, min(ring_count, ALARM_MAX_RINGS))

        try:
            interval_seconds = int(
                self.config.get(
                    CONF_ALARM_RING_INTERVAL_SECONDS, ALARM_RING_INTERVAL_SECONDS
                )
                or ALARM_RING_INTERVAL_SECONDS
            )
        except (TypeError, ValueError):
            interval_seconds = ALARM_RING_INTERVAL_SECONDS
        interval_seconds = max(5, min(interval_seconds, 120))

        async def _announce_cycle(_now=None) -> None:
            if state["stopped"]:
                return
            await self._async_announce(alarm)
            state["rings_done"] += 1
            if state["stopped"]:
                return
            if state["rings_done"] >= max_rings:
                self._stop_ringing(alarm_id)
                await self._async_send_alarm_clear()
                return
            state["repeat_unsub"] = async_call_later(
                self.hass, interval_seconds, _announce_cycle
            )

        await _announce_cycle()

        # Recurring alarms reschedule for their next occurrence; one-shot alarms are removed.
        if alarm.get("days"):
            next_trigger = self._resolve_next_trigger(
                alarm["hour"], alarm["minute"], alarm["days"]
            )
            alarm["next_trigger"] = next_trigger.isoformat()
            self._schedule(alarm_id, alarm)
        else:
            self._alarms.pop(alarm_id, None)
            self._unschedule(alarm_id)
        await self._async_save()
        self._notify_alarms_updated()

    def _resolve_sound_url(self) -> str | None:
        """Resolve the effective alarm sound URL: custom override, or a bundled sound."""
        custom = self.config.get(CONF_ALARM_SOUND_URL)
        if custom:
            return custom

        sound_key = self.config.get(CONF_ALARM_SOUND, "beep")
        if sound_key == ALARM_SOUND_NONE:
            return None

        relative_path = BUILTIN_ALARM_SOUNDS.get(sound_key)
        if not relative_path:
            return None

        try:
            base_url = get_url(self.hass, prefer_external=False)
        except NoURLAvailableError:
            _LOGGER.warning(
                "No internal/external URL configured for Home Assistant; "
                "alarm will announce without a preroll sound"
            )
            return None
        return f"{base_url}{relative_path}"

    async def _async_ring_target(
        self, entity_id: str, message: str, sound_url: str | None, blocking: bool
    ) -> None:
        """Ring on the target entity, using the right service for its domain."""
        domain = entity_id.split(".", 1)[0]

        if domain == "assist_satellite":
            service_data = {"entity_id": entity_id, "message": message}
            if sound_url:
                service_data["media_id"] = sound_url
            await self.hass.services.async_call(
                "assist_satellite", "announce", service_data, blocking=blocking
            )
            return

        # media_player (or anything else): just play the chime sound.
        if sound_url:
            await self.hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": entity_id,
                    "media_content_id": sound_url,
                    "media_content_type": "music",
                },
                blocking=blocking,
            )
        else:
            _LOGGER.warning(
                "No sound configured for media_player target %s; nothing to play",
                entity_id,
            )

    def _has_voice_satellite_card(self) -> bool:
        """Heuristic: is the jxlarrea Voice Satellite card/integration loaded?

        Used to decide whether it's safe to send the ALARM_RING/ALARM_CLEAR
        markers — only that specific card's frontend understands them; a
        real hardware assist_satellite (Voice PE, ESPHome) would otherwise
        speak/display the raw marker text.
        """
        return self.hass.services.has_service("voice_satellite", "wake")

    async def _async_announce(self, alarm: dict, message: str | None = None) -> None:
        """Play the alarm sound/announcement on the configured target entity."""
        target_entity = self.config.get(CONF_ALARM_SATELLITE_ENTITY)
        if not target_entity:
            _LOGGER.warning("No alarm target entity configured; cannot ring alarm")
            return

        if message is None:
            label = alarm.get("label")
            message = (
                f"This is your alarm: {label}." if label else "Wake up! This is your alarm."
            )

        is_voice_satellite_domain = target_entity.split(".", 1)[0] == "assist_satellite"
        if is_voice_satellite_domain and self._has_voice_satellite_card():
            message = f"ALARM_RING {alarm.get('label', '')}".rstrip()

        sound_url = self._resolve_sound_url()

        try:
            await self._async_ring_target(target_entity, message, sound_url, blocking=False)
        except Exception as e:
            _LOGGER.error("Failed to ring alarm on %s: %s", target_entity, e)

    async def async_test_ring(self) -> dict:
        """Trigger a real ring immediately for testing.

        Enters the full ringing state (binary_sensor turns on, the Voice
        Satellite card shows its visual alarm overlay) exactly like a
        scheduled alarm, so users can confirm both the sound AND the visual.
        Stop it with the Stop / Snooze buttons, "Nabu, stop", or the
        stop_alarm service.
        """
        target_entity = self.config.get(CONF_ALARM_SATELLITE_ENTITY)
        if not target_entity:
            return {"ok": False, "error": "No alarm target entity configured."}

        if self.hass.states.get(target_entity) is None:
            return {"ok": False, "error": f"Entity {target_entity} was not found."}

        now = dt_util.now()
        test_id = str(self._next_id)
        self._next_id += 1
        alarm = {
            "id": test_id,
            "hour": now.hour,
            "minute": now.minute,
            "label": "Test",
            "days": None,
            "next_trigger": now.isoformat(),
        }
        self._alarms[test_id] = alarm

        try:
            await self._async_ring(test_id)
        except Exception as e:
            self._alarms.pop(test_id, None)
            return {"ok": False, "error": str(e)}

        return {"ok": True, "entity_id": target_entity, "ringing": self.is_ringing()}

    async def async_shutdown(self) -> None:
        """Cancel all scheduled and in-progress ring timers on unload."""
        for alarm_id in list(self._unsub_schedule):
            self._unschedule(alarm_id)
        for alarm_id in list(self._ringing):
            self._stop_ringing(alarm_id)
