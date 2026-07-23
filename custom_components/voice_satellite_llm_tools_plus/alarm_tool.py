"""Alarm tools: set, list, cancel, and stop voice assistant alarms."""

import logging
import re

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .alarm_manager import AlarmManager
from .base_tool import BaseTool

_LOGGER = logging.getLogger(__name__)

DAY_NAME_TO_WEEKDAY = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def _parse_time(value: str) -> tuple[int, int]:
    """Parse a 24-hour HH:MM string into (hour, minute)."""
    match = TIME_RE.match(value.strip())
    if not match:
        raise ValueError(f"Invalid time format: {value!r}. Expected 24-hour HH:MM.")
    return int(match.group(1)), int(match.group(2))


def _parse_days(days: list[str] | None) -> list[int] | None:
    """Convert a list of weekday names to weekday numbers, or None for a one-time alarm."""
    if not days:
        return None
    resolved = [DAY_NAME_TO_WEEKDAY[d.lower()] for d in days if d.lower() in DAY_NAME_TO_WEEKDAY]
    return resolved or None


class BaseAlarmTool(BaseTool):
    """Base class for alarm tools, holding a reference to the shared AlarmManager."""

    def __init__(self, config: dict, hass: HomeAssistant, manager: AlarmManager) -> None:
        """Initialize with the entry's config and its AlarmManager."""
        super().__init__(config, hass)
        self.manager = manager


class SetAlarmTool(BaseAlarmTool):
    """Schedule a new alarm."""

    name = "set_alarm"
    description = (
        "Schedule an alarm that will ring on the voice satellite at a specific "
        "time. Use 24-hour HH:MM format for the time. For a recurring alarm, "
        "provide the days of the week it should repeat on; omit days for a "
        "one-time alarm that fires the next time that clock time occurs."
    )
    parameters = vol.Schema(
        {
            vol.Required(
                "time",
                description="24-hour time in HH:MM format, e.g. '07:30' or '22:00'.",
            ): str,
            vol.Optional(
                "label",
                description="A short label for the alarm, e.g. 'wake up' or 'take medicine'.",
            ): str,
            vol.Optional(
                "days",
                description=(
                    "Days of the week to repeat this alarm on. Omit for a "
                    "one-time alarm."
                ),
            ): [vol.In(list(DAY_NAME_TO_WEEKDAY))],
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
            hour, minute = _parse_time(tool_input.tool_args["time"])
        except ValueError as e:
            return {"error": str(e)}

        label = tool_input.tool_args.get("label", "")
        days = _parse_days(tool_input.tool_args.get("days"))

        alarm = await self.manager.async_set_alarm(hour, minute, label, days)
        return {
            "status": "scheduled",
            "alarm_id": alarm["id"],
            "time": f"{hour:02d}:{minute:02d}",
            "label": label,
            "recurring": bool(days),
            "next_trigger": alarm["next_trigger"],
            "instruction": "Confirm the alarm naturally, mentioning the time and label if given.",
        }


class ListAlarmsTool(BaseAlarmTool):
    """List all scheduled alarms."""

    name = "list_alarms"
    description = "List all currently scheduled alarms."
    parameters = vol.Schema({})

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the list_alarms tool."""
        alarms = self.manager.async_list_alarms()
        if not alarms:
            return {"alarms": [], "message": "No alarms are currently scheduled."}

        return {
            "alarms": [
                {
                    "alarm_id": a["id"],
                    "time": f"{a['hour']:02d}:{a['minute']:02d}",
                    "label": a.get("label", ""),
                    "recurring": bool(a.get("days")),
                    "next_trigger": a["next_trigger"],
                }
                for a in alarms
            ],
            "instruction": "Summarize the alarms naturally, in time order.",
        }


class CancelAlarmTool(BaseAlarmTool):
    """Cancel one or all scheduled alarms."""

    name = "cancel_alarm"
    description = (
        "Cancel a previously scheduled alarm by its alarm_id, or cancel all "
        "alarms at once by passing 'all'. Use list_alarms first if you don't "
        "already know the alarm_id."
    )
    parameters = vol.Schema(
        {
            vol.Required(
                "alarm_id",
                description="The alarm_id to cancel, or 'all' to cancel every alarm.",
            ): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the cancel_alarm tool."""
        alarm_id = tool_input.tool_args["alarm_id"]
        cancelled = await self.manager.async_cancel_alarm(alarm_id)
        if not cancelled:
            return {"error": f"No alarm found with id {alarm_id!r}."}
        return {"status": "cancelled", "alarm_id": alarm_id}


class TestAlarmTool(BaseAlarmTool):
    """Play a one-time test of the alarm sound and announcement."""

    name = "test_alarm"
    description = (
        "Immediately play a one-time test of the alarm sound and spoken "
        "announcement on the configured voice satellite, so the user can "
        "hear how it sounds and confirm which device it plays on. Use this "
        "when the user asks to test, try, or preview the alarm."
    )
    parameters = vol.Schema({})

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the test_alarm tool."""
        result = await self.manager.async_test_ring()
        if not result["ok"]:
            return {"error": result["error"]}
        return {
            "status": "played",
            "entity_id": result["entity_id"],
            "used_sound": bool(result.get("sound_url")),
            "instruction": "Ask the user if they heard it clearly and on the right device.",
        }


class StopAlarmTool(BaseAlarmTool):
    """Stop an alarm that is currently ringing."""

    name = "stop_alarm"
    description = (
        "Stop or silence an alarm that is ringing right now, e.g. when the "
        "user says 'stop', 'silence the alarm', 'turn it off', or 'Nabu, "
        "stop'. Call this immediately when the user asks to stop a ringing "
        "alarm, without asking for confirmation."
    )
    parameters = vol.Schema({})

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the stop_alarm tool."""
        stopped = await self.manager.async_stop_ringing()
        if not stopped:
            return {"status": "not_ringing", "message": "No alarm is currently ringing."}
        return {"status": "stopped"}
