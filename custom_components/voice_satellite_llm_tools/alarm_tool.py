"""Alarm tools for Voice Satellite LLM Tools, powered by Wakey."""

from __future__ import annotations

import logging
import re
from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.util import dt as dt_util

from .base_tool import BaseTool
from .const import (
    CONF_ALARM_DEFAULT_AUTO_DISMISS_MINUTES,
    CONF_ALARM_DEFAULT_MEDIA_PLAYER,
    CONF_ALARM_DEFAULT_REPEAT_COUNT,
    CONF_ALARM_DEFAULT_SNOOZE_MINUTES,
    CONF_ALARM_DEFAULT_SOUND_URI,
    CONF_ALARM_DEFAULT_VOLUME,
    DEFAULT_ALARM_AUTO_DISMISS_MINUTES,
    DEFAULT_ALARM_MEDIA_PLAYER,
    DEFAULT_ALARM_REPEAT_COUNT,
    DEFAULT_ALARM_SNOOZE_MINUTES,
    DEFAULT_ALARM_SOUND_URI,
    DEFAULT_ALARM_VOLUME,
)

_LOGGER = logging.getLogger(__name__)

DAY_NAME_TO_WEEKDAY = {
    # English
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
    # Spanish
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6,
}

SPECIAL_DAY_GROUPS = {
    "weekdays": [0, 1, 2, 3, 4],
    "laborables": [0, 1, 2, 3, 4],
    "dias laborables": [0, 1, 2, 3, 4],
    "días laborables": [0, 1, 2, 3, 4],
    "entre semana": [0, 1, 2, 3, 4],
    "weekends": [5, 6],
    "fin de semana": [5, 6],
    "fines de semana": [5, 6],
    "daily": [0, 1, 2, 3, 4, 5, 6],
    "everyday": [0, 1, 2, 3, 4, 5, 6],
    "todos los dias": [0, 1, 2, 3, 4, 5, 6],
    "todos los días": [0, 1, 2, 3, 4, 5, 6],
    "diario": [0, 1, 2, 3, 4, 5, 6],
}

WEEKDAY_NAMES_EN = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

TIME_RE = re.compile(
    r"^\s*(\d{1,2})(?::(\d{2}))?(?::(\d{2}))?\s*([ap]\.?m\.?)?\s*$",
    re.IGNORECASE,
)


def parse_time_str(value: str) -> tuple[int, int]:
    """Parse time string into (hour, minute). Supports 24h and 12h AM/PM."""
    m = TIME_RE.match(str(value).strip())
    if not m:
        raise ValueError(
            f"Invalid time format: {value!r}. Expected HH:MM or 12-hour AM/PM format (e.g. '07:30' or '7:30 AM')."
        )
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(4)
    if ampm:
        is_pm = "p" in ampm.lower()
        if is_pm and hour < 12:
            hour += 12
        elif not is_pm and hour == 12:
            hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Time out of range: {hour:02d}:{minute:02d}")
    return hour, minute


def parse_days_input(days: Any) -> list[int] | None:
    """Parse a list or string of day names into sorted list of weekday integers [0..6]."""
    if not days:
        return None
    if isinstance(days, str):
        days = [d.strip() for d in days.split(",") if d.strip()]
    resolved: set[int] = set()
    for d in days:
        if not isinstance(d, str):
            continue
        clean = d.strip().lower()
        if clean in SPECIAL_DAY_GROUPS:
            resolved.update(SPECIAL_DAY_GROUPS[clean])
        elif clean in DAY_NAME_TO_WEEKDAY:
            resolved.add(DAY_NAME_TO_WEEKDAY[clean])
    return sorted(resolved) if resolved else None


def get_wakey_data(hass: HomeAssistant) -> Any | None:
    """Retrieve the WakeyData runtime instance if Wakey is installed and loaded."""
    entries = hass.data.get("wakey", {})
    return next(iter(entries.values()), None)


def get_default_media_player(hass: HomeAssistant, config: dict) -> str:
    """Resolve default media player entity."""
    configured = config.get(CONF_ALARM_DEFAULT_MEDIA_PLAYER)
    if configured and hass.states.get(configured):
        return configured
    wakey_data = get_wakey_data(hass)
    if wakey_data:
        alarms = wakey_data.store.async_all()
        for a in alarms:
            if a.media_player and hass.states.get(a.media_player):
                return a.media_player
    for state in hass.states.async_all():
        if state.domain == "media_player":
            return state.entity_id
    return configured or "media_player.voice_satellite"


def build_alarm_card(hass: HomeAssistant, alarm_entries: list[dict] | None = None) -> dict:
    """Build a Lovelace card config for Voice Satellite card media panel."""
    entities = []
    if hass.states.get("binary_sensor.wakey_ringing"):
        entities.append("binary_sensor.wakey_ringing")
    if hass.states.get("sensor.wakey_next_alarm"):
        entities.append("sensor.wakey_next_alarm")

    for state in hass.states.async_all():
        if state.domain in ("switch", "time") and "alarm" in state.entity_id:
            if state.entity_id not in entities:
                entities.append(state.entity_id)

    if entities:
        return {
            "type": "entities",
            "title": "Alarms",
            "entities": entities[:8],
        }

    if alarm_entries:
        lines = [
            f"- **{a.get('time', '')}**: {a.get('name', 'Alarm')} ({a.get('repeat', 'once')})"
            for a in alarm_entries
        ]
        return {
            "type": "markdown",
            "title": "Alarms",
            "content": "\n".join(lines),
        }

    return {"type": "markdown", "title": "Alarms", "content": "No alarms scheduled."}


class BaseAlarmTool(BaseTool):
    """Base tool providing shared helpers for Wakey alarm operations."""

    def __init__(self, config: dict, hass: HomeAssistant) -> None:
        """Initialize the base alarm tool."""
        super().__init__(config, hass)

    def _get_wakey(self) -> Any | None:
        return get_wakey_data(self.hass)


class SetAlarmTool(BaseAlarmTool):
    """Schedule a new alarm using Wakey."""

    name = "set_alarm"
    description = (
        "Schedule an alarm that will ring on the smart speaker or satellite at a "
        "specific time. Use 24-hour HH:MM format (or 12-hour AM/PM format) for the time. "
        "For a recurring alarm, provide the days of the week it should repeat on "
        "(e.g. ['monday', 'friday'], Spanish ['lunes', 'viernes'], or 'weekdays', 'weekends', 'daily'); "
        "omit days for a one-time alarm that fires the next time that clock time occurs."
    )
    parameters = vol.Schema(
        {
            vol.Required(
                "time",
                description="Time in HH:MM (e.g. '07:30', '7:00 AM', or '22:00').",
            ): str,
            vol.Optional(
                "label",
                description="Short label or name for the alarm (e.g. 'wake up', 'medicine', 'work').",
            ): str,
            vol.Optional(
                "days",
                description=(
                    "Days of the week to repeat this alarm on (e.g. ['monday', 'wednesday'], "
                    "'weekdays', 'laborables', 'daily'). Omit for a one-time alarm."
                ),
            ): vol.Any([str], str),
            vol.Optional(
                "media_player",
                description="Target media player entity ID (e.g. 'media_player.bedroom_speaker').",
            ): str,
            vol.Optional(
                "volume",
                description="Alarm volume from 0.0 to 1.0 (default 0.7).",
            ): vol.Coerce(float),
            vol.Optional(
                "repeat_count",
                description="How many times the alarm sound loops (0 = loop continuously until stopped).",
            ): vol.Coerce(int),
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the set_alarm tool."""
        try:
            hour, minute = parse_time_str(tool_input.tool_args["time"])
        except ValueError as e:
            return {"error": str(e)}

        time_formatted = f"{hour:02d}:{minute:02d}"
        label = (tool_input.tool_args.get("label") or "Alarm").strip()
        weekdays = parse_days_input(tool_input.tool_args.get("days"))

        # Resolve media player, volume, repeat_count, source_uri
        media_player = tool_input.tool_args.get("media_player")
        if not media_player or not media_player.startswith("media_player."):
            media_player = get_default_media_player(hass, self.config)

        volume = tool_input.tool_args.get("volume")
        if volume is None:
            volume = float(self.config.get(CONF_ALARM_DEFAULT_VOLUME, DEFAULT_ALARM_VOLUME))
        volume = min(1.0, max(0.0, volume))

        repeat_count = tool_input.tool_args.get("repeat_count")
        if repeat_count is None:
            repeat_count = int(
                self.config.get(CONF_ALARM_DEFAULT_REPEAT_COUNT, DEFAULT_ALARM_REPEAT_COUNT)
            )

        source_uri = self.config.get(CONF_ALARM_DEFAULT_SOUND_URI, DEFAULT_ALARM_SOUND_URI)
        snooze_minutes = int(
            self.config.get(CONF_ALARM_DEFAULT_SNOOZE_MINUTES, DEFAULT_ALARM_SNOOZE_MINUTES)
        )
        auto_dismiss = int(
            self.config.get(
                CONF_ALARM_DEFAULT_AUTO_DISMISS_MINUTES, DEFAULT_ALARM_AUTO_DISMISS_MINUTES
            )
        )

        now_local = dt_util.now()

        if weekdays:
            repeat = "weekly"
            date_str = None
        else:
            repeat = "once"
            alarm_clock = time(hour, minute)
            if alarm_clock <= now_local.time():
                date_str = (now_local.date() + timedelta(days=1)).isoformat()
            else:
                date_str = now_local.date().isoformat()

        wakey_data = self._get_wakey()
        if wakey_data:
            for a in wakey_data.store.async_all():
                if a.time == time_formatted:
                    if (weekdays and a.weekdays == weekdays) or (not weekdays and a.repeat == "once"):
                        if a.enabled:
                            return {
                                "status": "already_exists",
                                "alarm_id": a.id,
                                "time": time_formatted,
                                "label": a.name,
                                "repeat": a.repeat,
                                "days": ", ".join(WEEKDAY_NAMES_EN[d] for d in weekdays) if weekdays else (date_str or "next occurrence"),
                                "media_player": a.media_player or media_player,
                                "card": build_alarm_card(hass),
                                "instruction": f"Inform the user that an alarm is already configured for {time_formatted}.",
                            }
                        wakey_data.store.async_update(a.id, {"enabled": True})
                        return {
                            "status": "reactivated",
                            "alarm_id": a.id,
                            "time": time_formatted,
                            "label": a.name,
                            "repeat": a.repeat,
                            "days": ", ".join(WEEKDAY_NAMES_EN[d] for d in weekdays) if weekdays else (date_str or "next occurrence"),
                            "media_player": a.media_player or media_player,
                            "card": build_alarm_card(hass),
                            "instruction": f"Confirm that the existing alarm for {time_formatted} has been re-enabled.",
                        }

        payload = {
            "name": label,
            "time": time_formatted,
            "repeat": repeat,
            "weekdays": weekdays if weekdays is not None else [],
            "media_player": media_player,
            "source_uri": source_uri,
            "source_kind": "media_player",
            "volume": volume,
            "repeat_count": repeat_count,
            "snooze_minutes": snooze_minutes,
            "auto_dismiss_minutes": auto_dismiss,
            "enabled": True,
        }
        if date_str:
            payload["date"] = date_str

        created_alarm = None

        if wakey_data:
            try:
                created_alarm = wakey_data.store.async_create(payload)
            except Exception as e:
                _LOGGER.exception("Error creating alarm directly in Wakey store: %s", e)

        if created_alarm is None:
            try:
                await hass.services.async_call("wakey", "create", payload, blocking=True)
            except Exception as e:
                _LOGGER.exception("Error calling wakey.create service: %s", e)
                return {"error": f"Failed to schedule alarm: {e}"}

        alarm_id = created_alarm.id if created_alarm else "new"
        day_summary = (
            ", ".join(WEEKDAY_NAMES_EN[d] for d in weekdays) if weekdays else (date_str or "next occurrence")
        )

        return {
            "status": "scheduled",
            "alarm_id": alarm_id,
            "time": time_formatted,
            "label": label,
            "repeat": repeat,
            "days": day_summary,
            "media_player": media_player,
            "card": build_alarm_card(hass),
            "instruction": "Confirm the alarm naturally in speech, mentioning the time and label.",
        }


class ListAlarmsTool(BaseAlarmTool):
    """List all scheduled Wakey alarms."""

    name = "list_alarms"
    description = (
        "List all scheduled alarms, their trigger times, recurrence, and whether "
        "any alarm is currently ringing or snoozed."
    )
    parameters = vol.Schema({})

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the list_alarms tool."""
        wakey_data = self._get_wakey()
        if not wakey_data:
            return {
                "alarms": [],
                "message": "Wakey integration is not available or has no active alarms.",
            }

        alarms = wakey_data.store.async_all()
        if not alarms:
            return {"alarms": [], "message": "No alarms are currently scheduled."}

        ringing_dict = wakey_data.player.ringing
        res_list = []

        for a in alarms:
            next_fire = wakey_data.scheduler.async_next_fire(a)
            is_active_ringing = a.id in ringing_dict and not ringing_dict[a.id].snoozed
            is_active_snoozed = a.id in ringing_dict and ringing_dict[a.id].snoozed
            days_labels = [WEEKDAY_NAMES_EN[d] for d in a.weekdays] if a.repeat == "weekly" else []

            res_list.append(
                {
                    "alarm_id": a.id,
                    "time": a.time,
                    "label": a.name,
                    "enabled": a.enabled,
                    "repeat": a.repeat,
                    "days": days_labels,
                    "next_trigger": next_fire.isoformat() if next_fire else None,
                    "is_ringing": is_active_ringing,
                    "is_snoozed": is_active_snoozed,
                }
            )

        return {
            "alarms": res_list,
            "count": len(res_list),
            "card": build_alarm_card(hass, res_list),
            "instruction": "Summarize the scheduled alarms naturally in chronological order.",
        }


class CancelAlarmTool(BaseAlarmTool):
    """Cancel or delete scheduled Wakey alarms."""

    name = "cancel_alarm"
    description = (
        "Cancel or delete one or all scheduled alarms. You can specify the alarm by "
        "alarm_id, by time (e.g. '07:00' or '7 AM'), by label (e.g. 'work'), "
        "or pass cancel_all=True (or alarm_id='all') to delete every alarm."
    )
    parameters = vol.Schema(
        {
            vol.Optional(
                "alarm_id",
                description="The alarm_id to cancel, or 'all' to cancel all alarms.",
            ): str,
            vol.Optional(
                "time",
                description="Time of the alarm to cancel (e.g. '07:30' or '7:30 AM').",
            ): str,
            vol.Optional(
                "label",
                description="Label/name of the alarm to cancel.",
            ): str,
            vol.Optional(
                "cancel_all",
                description="Set to true to cancel every scheduled alarm.",
            ): bool,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the cancel_alarm tool."""
        wakey_data = self._get_wakey()
        if not wakey_data:
            return {"error": "Wakey integration is not loaded."}

        cancel_all = tool_input.tool_args.get("cancel_all", False)
        alarm_id = tool_input.tool_args.get("alarm_id", "").strip()
        time_arg = tool_input.tool_args.get("time")
        label_arg = (tool_input.tool_args.get("label") or "").strip().lower()

        alarms = wakey_data.store.async_all()
        if not alarms:
            return {"status": "none_found", "message": "No alarms are currently scheduled."}

        # Cancel all
        if cancel_all or alarm_id.lower() == "all":
            count = len(alarms)
            for a in list(alarms):
                wakey_data.store.async_delete(a.id)
            return {
                "status": "cancelled_all",
                "count": count,
                "message": f"Cancelled all {count} alarms.",
                "card": build_alarm_card(hass),
            }

        # Match specific alarm(s)
        matched: list[Any] = []

        if alarm_id:
            for a in alarms:
                if a.id == alarm_id:
                    matched.append(a)

        if not matched and time_arg:
            try:
                h, m = parse_time_str(time_arg)
                target_time = f"{h:02d}:{m:02d}"
                for a in alarms:
                    if a.time == target_time:
                        matched.append(a)
            except ValueError:
                pass

        if not matched and label_arg:
            for a in alarms:
                if label_arg in a.name.lower() or a.name.lower() in label_arg:
                    matched.append(a)

        # If user didn't specify and there is exactly 1 alarm, cancel it
        if not matched and not alarm_id and not time_arg and not label_arg and len(alarms) == 1:
            matched.append(alarms[0])

        if not matched:
            return {
                "error": "No matching alarm found.",
                "available_alarms": [
                    {"alarm_id": a.id, "time": a.time, "label": a.name}
                    for a in alarms
                ],
            }

        deleted_info = []
        for a in matched:
            wakey_data.store.async_delete(a.id)
            deleted_info.append({"alarm_id": a.id, "time": a.time, "label": a.name})

        return {
            "status": "cancelled",
            "cancelled": deleted_info,
            "card": build_alarm_card(hass),
            "instruction": "Confirm the cancellation naturally in speech.",
        }


class SnoozeAlarmTool(BaseAlarmTool):
    """Snooze a ringing Wakey alarm."""

    name = "snooze_alarm"
    description = (
        "Snooze an alarm that is currently ringing. Defaults to 9 minutes unless specified."
    )
    parameters = vol.Schema(
        {
            vol.Optional(
                "minutes",
                description="Minutes to snooze (default 9, range 1-120).",
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=120)),
            vol.Optional(
                "alarm_id",
                description="Optional alarm_id if multiple alarms are ringing.",
            ): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the snooze_alarm tool."""
        minutes = tool_input.tool_args.get(
            "minutes",
            int(self.config.get(CONF_ALARM_DEFAULT_SNOOZE_MINUTES, DEFAULT_ALARM_SNOOZE_MINUTES)),
        )
        alarm_id = tool_input.tool_args.get("alarm_id")

        wakey_data = self._get_wakey()
        if wakey_data:
            if not wakey_data.player.any_ringing:
                return {
                    "status": "not_ringing",
                    "message": "No alarm is currently ringing to snooze.",
                }
            await wakey_data.player.async_snooze(alarm_id, minutes=minutes)
            return {
                "status": "snoozed",
                "minutes": minutes,
                "instruction": f"Inform the user the alarm is snoozed for {minutes} minutes.",
            }

        try:
            call_data = {"minutes": minutes}
            if alarm_id:
                call_data["alarm_id"] = alarm_id
            await hass.services.async_call("wakey", "snooze", call_data, blocking=True)
            return {"status": "snoozed", "minutes": minutes}
        except Exception as e:
            return {"error": f"Failed to snooze alarm: {e}"}


class StopAlarmTool(BaseAlarmTool):
    """Stop or silence an alarm that is currently ringing."""

    name = "stop_alarm"
    description = (
        "Stop or silence an alarm that is currently ringing (e.g. when the user says "
        "'stop', 'silence the alarm', 'turn it off', 'apagar alarma'). Call this immediately "
        "without asking for confirmation."
    )
    parameters = vol.Schema(
        {
            vol.Optional(
                "alarm_id",
                description="Optional alarm_id if multiple alarms are ringing.",
            ): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the stop_alarm tool."""
        alarm_id = tool_input.tool_args.get("alarm_id")
        wakey_data = self._get_wakey()

        if wakey_data:
            if not wakey_data.player.any_ringing:
                return {
                    "status": "not_ringing",
                    "message": "No alarm is currently ringing.",
                }
            await wakey_data.player.async_dismiss(alarm_id)
            return {"status": "stopped", "message": "Alarm stopped."}

        try:
            call_data = {}
            if alarm_id:
                call_data["alarm_id"] = alarm_id
            await hass.services.async_call("wakey", "dismiss", call_data, blocking=True)
            return {"status": "stopped"}
        except Exception as e:
            return {"error": f"Failed to stop alarm: {e}"}


class AdjustAlarmTool(BaseAlarmTool):
    """Adjust or change the time of an existing Wakey alarm."""

    name = "adjust_alarm"
    description = (
        "Change or adjust the time of an existing alarm for its next occurrence "
        "(e.g. 'move my 7 AM alarm to 7:30', 'change alarm to 8 AM')."
    )
    parameters = vol.Schema(
        {
            vol.Required(
                "time",
                description="New time in HH:MM (e.g. '07:30' or '8:00 AM').",
            ): str,
            vol.Optional(
                "alarm_id",
                description="The alarm_id of the alarm to adjust.",
            ): str,
            vol.Optional(
                "current_time",
                description="Current time of the alarm to adjust (e.g. '07:00').",
            ): str,
            vol.Optional(
                "label",
                description="Label of the alarm to adjust.",
            ): str,
            vol.Optional(
                "clear",
                description="If true, clear any previous adjustment and revert to normal schedule.",
            ): bool,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the adjust_alarm tool."""
        try:
            new_hour, new_minute = parse_time_str(tool_input.tool_args["time"])
        except ValueError as e:
            return {"error": str(e)}

        new_time_str = f"{new_hour:02d}:{new_minute:02d}"
        alarm_id = tool_input.tool_args.get("alarm_id")
        current_time_arg = tool_input.tool_args.get("current_time")
        label_arg = (tool_input.tool_args.get("label") or "").strip().lower()
        clear = tool_input.tool_args.get("clear", False)

        wakey_data = self._get_wakey()
        if not wakey_data:
            return {"error": "Wakey integration is not loaded."}

        alarms = wakey_data.store.async_all()
        target_alarm = None

        if alarm_id:
            for a in alarms:
                if a.id == alarm_id:
                    target_alarm = a
                    break

        if not target_alarm and current_time_arg:
            try:
                ch, cm = parse_time_str(current_time_arg)
                formatted_cur = f"{ch:02d}:{cm:02d}"
                for a in alarms:
                    if a.time == formatted_cur:
                        target_alarm = a
                        break
            except ValueError:
                pass

        if not target_alarm and label_arg:
            for a in alarms:
                if label_arg in a.name.lower() or a.name.lower() in label_arg:
                    target_alarm = a
                    break

        if not target_alarm and len(alarms) == 1:
            target_alarm = alarms[0]

        if not target_alarm:
            return {
                "error": "Could not identify which alarm to adjust.",
                "available_alarms": [
                    {"alarm_id": a.id, "time": a.time, "label": a.name}
                    for a in alarms
                ],
            }

        try:
            if clear:
                wakey_data.store.async_update(
                    target_alarm.id, {"override_for": None, "override_time": None}
                )
            else:
                patch = wakey_data.scheduler.async_plan_adjustment(target_alarm, new_time_str)
                wakey_data.store.async_update(target_alarm.id, patch)
        except Exception as e:
            return {"error": f"Failed to adjust alarm: {e}"}

        return {
            "status": "adjusted",
            "alarm_id": target_alarm.id,
            "label": target_alarm.name,
            "new_time": new_time_str,
            "card": build_alarm_card(hass),
            "instruction": f"Confirm that the {target_alarm.name} alarm has been adjusted to {new_time_str}.",
        }


class TestAlarmTool(BaseAlarmTool):
    """Test or preview an alarm sound on the configured media player."""

    name = "test_alarm"
    description = (
        "Test or preview an alarm sound immediately on the speaker/satellite so the user "
        "can hear how it sounds and check volume. Use when the user asks to test, try, "
        "or preview the alarm."
    )
    parameters = vol.Schema(
        {
            vol.Optional(
                "media_player",
                description="Optional media player entity ID to test on.",
            ): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the test_alarm tool."""
        media_player = tool_input.tool_args.get("media_player")
        if not media_player or not media_player.startswith("media_player."):
            media_player = get_default_media_player(hass, self.config)

        wakey_data = self._get_wakey()
        alarms = wakey_data.store.async_all() if wakey_data else []

        if wakey_data and alarms:
            # Trigger the first alarm as a live test
            test_alarm = alarms[0]
            await wakey_data.player.async_fire(test_alarm)
            return {
                "status": "playing",
                "alarm_id": test_alarm.id,
                "media_player": test_alarm.media_player,
                "instruction": "Ask the user if they can hear the alarm playing clearly.",
            }

        # Otherwise play the test sound via media_player service
        sound_uri = self.config.get(CONF_ALARM_DEFAULT_SOUND_URI, DEFAULT_ALARM_SOUND_URI)
        volume = float(self.config.get(CONF_ALARM_DEFAULT_VOLUME, DEFAULT_ALARM_VOLUME))

        try:
            await hass.services.async_call(
                "media_player",
                "volume_set",
                {"entity_id": media_player, "volume_level": volume},
                blocking=True,
            )
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": media_player,
                    "media_content_id": sound_uri,
                    "media_content_type": "music",
                },
                blocking=True,
            )
            return {
                "status": "playing",
                "media_player": media_player,
                "sound_uri": sound_uri,
                "instruction": "Ask the user if they can hear the alarm playing clearly.",
            }
        except Exception as e:
            return {"error": f"Failed to play test alarm on {media_player}: {e}"}
