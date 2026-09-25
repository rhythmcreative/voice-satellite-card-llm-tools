"""Unit tests for Alarm Tool (Wakey integration)."""

import asyncio
from datetime import datetime, time, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import zoneinfo

from custom_components.voice_satellite_llm_tools.alarm_tool import (
    AdjustAlarmTool,
    CancelAlarmTool,
    ListAlarmsTool,
    SetAlarmTool,
    SnoozeAlarmTool,
    StopAlarmTool,
    TestAlarmTool,
    build_alarm_card,
    get_default_media_player,
    parse_days_input,
    parse_time_str,
)
from custom_components.voice_satellite_llm_tools.const import (
    ALARM_API_ID,
    ALARM_API_NAME,
    CONF_TOOL_TYPE,
    DOMAIN,
    TOOL_TYPE_ALARM,
)
from custom_components.voice_satellite_llm_tools.llm_api import AlarmAPI, setup_llm_api


def test_parse_time():
    """Test parsing of 24h and 12h times."""
    assert parse_time_str("07:30") == (7, 30)
    assert parse_time_str("7:30") == (7, 30)
    assert parse_time_str("7:30 AM") == (7, 30)
    assert parse_time_str("7:30 PM") == (19, 30)
    assert parse_time_str("7 AM") == (7, 0)
    assert parse_time_str("7 PM") == (19, 0)
    assert parse_time_str("12 AM") == (0, 0)
    assert parse_time_str("12 PM") == (12, 0)
    assert parse_time_str("23:59") == (23, 59)
    assert parse_time_str("00:00") == (0, 0)
    assert parse_time_str("07:30:15") == (7, 30)

    try:
        parse_time_str("invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        parse_time_str("25:00")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_parse_days():
    """Test parsing English and Spanish weekdays and special groups."""
    assert parse_days_input(None) is None
    assert parse_days_input([]) is None
    assert parse_days_input(["monday", "friday"]) == [0, 4]
    assert parse_days_input(["lunes", "viernes"]) == [0, 4]
    assert parse_days_input(["miércoles", "sábado"]) == [2, 5]
    assert parse_days_input(["miercoles", "sabado"]) == [2, 5]
    assert parse_days_input(["weekdays"]) == [0, 1, 2, 3, 4]
    assert parse_days_input(["laborables"]) == [0, 1, 2, 3, 4]
    assert parse_days_input(["entre semana"]) == [0, 1, 2, 3, 4]
    assert parse_days_input(["weekends"]) == [5, 6]
    assert parse_days_input(["fines de semana"]) == [5, 6]
    assert parse_days_input(["daily"]) == [0, 1, 2, 3, 4, 5, 6]
    assert parse_days_input(["todos los días"]) == [0, 1, 2, 3, 4, 5, 6]
    assert parse_days_input("lunes, miércoles, viernes") == [0, 2, 4]


def test_alarm_tools_init():
    """Test tool initialization and attributes."""
    hass = MagicMock()
    config = {}

    t_set = SetAlarmTool(config, hass)
    assert t_set.name == "set_alarm"

    t_list = ListAlarmsTool(config, hass)
    assert t_list.name == "list_alarms"

    t_cancel = CancelAlarmTool(config, hass)
    assert t_cancel.name == "cancel_alarm"

    t_snooze = SnoozeAlarmTool(config, hass)
    assert t_snooze.name == "snooze_alarm"

    t_stop = StopAlarmTool(config, hass)
    assert t_stop.name == "stop_alarm"

    t_adjust = AdjustAlarmTool(config, hass)
    assert t_adjust.name == "adjust_alarm"

    t_test = TestAlarmTool(config, hass)
    assert t_test.name == "test_alarm"


def run_async(coro):
    return asyncio.run(coro)


def test_set_alarm_tool():
    """Test set_alarm tool execution."""
    hass = MagicMock()
    hass.config.as_time_zone.return_value = timezone.utc
    hass.states.async_all.return_value = []
    hass.states.get.return_value = None

    mock_alarm = MagicMock()
    mock_alarm.id = "alarm_123"
    mock_alarm.name = "Work"
    mock_alarm.time = "07:30"

    mock_wakey = MagicMock()
    mock_wakey.store.async_create.return_value = mock_alarm
    mock_wakey.store.async_all.return_value = []
    hass.data = {"wakey": {"entry_1": mock_wakey}}

    tool = SetAlarmTool({}, hass)
    tool_input = MagicMock()
    tool_input.tool_args = {
        "time": "07:30 AM",
        "label": "Work",
        "days": ["monday", "tuesday"],
        "media_player": "media_player.bedroom",
        "volume": 0.8,
    }

    result = run_async(tool.async_call(hass, tool_input, MagicMock()))
    assert result["status"] == "scheduled"
    assert result["alarm_id"] == "alarm_123"
    assert result["time"] == "07:30"
    assert result["label"] == "Work"
    assert result["repeat"] == "weekly"

    # Verify payload passed to store
    payload = mock_wakey.store.async_create.call_args[0][0]
    assert payload["time"] == "07:30"
    assert payload["repeat"] == "weekly"
    assert payload["weekdays"] == [0, 1]
    assert payload["volume"] == 0.8


def test_set_alarm_duplicate_prevention():
    """Test that setting an alarm for an existing time returns already_exists and does not duplicate."""
    hass = MagicMock()
    hass.states.async_all.return_value = []
    hass.states.get.return_value = None

    existing_alarm = MagicMock()
    existing_alarm.id = "alarm_existing"
    existing_alarm.name = "Work"
    existing_alarm.time = "07:30"
    existing_alarm.repeat = "weekly"
    existing_alarm.weekdays = [0, 1]
    existing_alarm.enabled = True
    existing_alarm.media_player = "media_player.bedroom"

    mock_wakey = MagicMock()
    mock_wakey.store.async_all.return_value = [existing_alarm]
    hass.data = {"wakey": {"entry_1": mock_wakey}}

    tool = SetAlarmTool({}, hass)
    tool_input = MagicMock()
    tool_input.tool_args = {
        "time": "07:30",
        "days": ["monday", "tuesday"],
    }

    result = run_async(tool.async_call(hass, tool_input, MagicMock()))
    assert result["status"] == "already_exists"
    assert result["alarm_id"] == "alarm_existing"
    mock_wakey.store.async_create.assert_not_called()


def test_list_alarms_tool():
    """Test list_alarms tool execution."""
    hass = MagicMock()
    mock_alarm = MagicMock()
    mock_alarm.id = "alarm_1"
    mock_alarm.name = "Morning"
    mock_alarm.time = "08:00"
    mock_alarm.enabled = True
    mock_alarm.repeat = "once"
    mock_alarm.weekdays = []

    mock_wakey = MagicMock()
    mock_wakey.store.async_all.return_value = [mock_alarm]
    mock_wakey.scheduler.async_next_fire.return_value = datetime(2026, 9, 26, 8, 0, tzinfo=timezone.utc)
    mock_wakey.player.ringing = {}
    hass.data = {"wakey": {"entry_1": mock_wakey}}
    hass.states.async_all.return_value = []
    hass.states.get.return_value = None

    tool = ListAlarmsTool({}, hass)
    result = run_async(tool.async_call(hass, MagicMock(), MagicMock()))
    assert result["count"] == 1
    assert result["alarms"][0]["alarm_id"] == "alarm_1"
    assert result["alarms"][0]["time"] == "08:00"
    assert result["alarms"][0]["is_ringing"] is False


def test_cancel_alarm_tool():
    """Test cancel_alarm tool execution."""
    hass = MagicMock()
    mock_alarm1 = MagicMock()
    mock_alarm1.id = "alarm_1"
    mock_alarm1.name = "Work"
    mock_alarm1.time = "07:00"

    mock_alarm2 = MagicMock()
    mock_alarm2.id = "alarm_2"
    mock_alarm2.name = "Weekend"
    mock_alarm2.time = "09:00"

    mock_wakey = MagicMock()
    mock_wakey.store.async_all.return_value = [mock_alarm1, mock_alarm2]
    hass.data = {"wakey": {"entry_1": mock_wakey}}
    hass.states.async_all.return_value = []
    hass.states.get.return_value = None

    tool = CancelAlarmTool({}, hass)

    # Cancel by time
    tool_input = MagicMock()
    tool_input.tool_args = {"time": "7:00 AM"}
    result = run_async(tool.async_call(hass, tool_input, MagicMock()))
    assert result["status"] == "cancelled"
    mock_wakey.store.async_delete.assert_called_with("alarm_1")

    # Cancel all
    tool_input.tool_args = {"cancel_all": True}
    result = run_async(tool.async_call(hass, tool_input, MagicMock()))
    assert result["status"] == "cancelled_all"
    assert result["count"] == 2


def test_snooze_and_stop_alarm_tools():
    """Test snooze_alarm and stop_alarm tools."""
    hass = MagicMock()
    mock_wakey = MagicMock()
    mock_wakey.player.any_ringing = True
    mock_wakey.player.async_snooze = AsyncMock()
    mock_wakey.player.async_dismiss = AsyncMock()
    hass.data = {"wakey": {"entry_1": mock_wakey}}

    # Snooze
    t_snooze = SnoozeAlarmTool({}, hass)
    tool_input = MagicMock()
    tool_input.tool_args = {"minutes": 15}
    res_snooze = run_async(t_snooze.async_call(hass, tool_input, MagicMock()))
    assert res_snooze["status"] == "snoozed"
    assert res_snooze["minutes"] == 15
    mock_wakey.player.async_snooze.assert_awaited_once_with(None, minutes=15)

    # Stop
    t_stop = StopAlarmTool({}, hass)
    tool_input.tool_args = {}
    res_stop = run_async(t_stop.async_call(hass, tool_input, MagicMock()))
    assert res_stop["status"] == "stopped"
    mock_wakey.player.async_dismiss.assert_awaited_once_with(None)


def test_alarm_api_registration():
    """Test AlarmAPI initialization and registration."""
    hass = MagicMock()
    hass.data = {}
    config_data = {CONF_TOOL_TYPE: TOOL_TYPE_ALARM}

    with patch("homeassistant.helpers.llm.async_register_api") as mock_reg:
        mock_reg.return_value = MagicMock()
        run_async(setup_llm_api(hass, config_data, "entry_alarm"))
        assert mock_reg.called
        api = mock_reg.call_args[0][1]
        assert isinstance(api, AlarmAPI)
        assert api.id == ALARM_API_ID
        assert api.name == ALARM_API_NAME


def test_build_alarm_card():
    """Test build_alarm_card returns native Lovelace cards."""
    hass = MagicMock()
    hass.states.get.return_value = None
    hass.states.async_all.return_value = []

    # Single alarm scheduled
    card = build_alarm_card(
        hass,
        highlight_alarm={"alarm_id": "a1", "label": "Morning", "time": "07:00"},
        action="scheduled",
    )
    assert card["type"] == "tile"
    assert card["name"] == "Morning • 07:00"
    assert card["icon"] == "mdi:alarm-check"
    assert card["color"] == "green"

    # Single alarm cancelled
    card_cancel = build_alarm_card(
        hass,
        highlight_alarm={"alarm_id": "a1", "label": "Morning", "time": "07:00"},
        action="cancelled",
    )
    assert card_cancel["type"] == "tile"
    assert card_cancel["name"] == "Morning (Cancelada)"
    assert card_cancel["icon"] == "mdi:alarm-off"
    assert card_cancel["color"] == "red"

    # List of multiple alarms -> entities card
    card_list_multi = build_alarm_card(
        hass,
        alarm_entries=[
            {"alarm_id": "a1", "name": "Work", "time": "07:00", "enabled": True},
            {"alarm_id": "a2", "name": "Gym", "time": "18:00", "enabled": False},
        ],
        action="list",
    )
    assert card_list_multi["type"] == "entities"
    assert card_list_multi["title"] == "Alarmas"
    assert len(card_list_multi["entities"]) == 2
    assert card_list_multi["entities"][0]["name"] == "Work • 07:00"
    assert card_list_multi["entities"][0]["icon"] == "mdi:alarm"
    assert card_list_multi["entities"][1]["name"] == "Gym • 18:00"
    assert card_list_multi["entities"][1]["icon"] == "mdi:alarm-off"

    # List of 1 alarm -> tile card
    card_list_single = build_alarm_card(
        hass,
        alarm_entries=[{"alarm_id": "a1", "name": "Work", "time": "07:00"}],
        action="list",
    )
    assert card_list_single["type"] == "tile"
    assert card_list_single["name"] == "Work • 07:00"

    # List with 0 alarms -> tile card empty state
    card_list_empty = build_alarm_card(hass, alarm_entries=[], action="list")
    assert card_list_empty["type"] == "tile"
    assert card_list_empty["name"] == "Sin alarmas programadas"
    assert card_list_empty["icon"] == "mdi:alarm-off"


if __name__ == "__main__":
    print("Running tests...")
    test_parse_time()
    test_parse_days()
    test_alarm_tools_init()
    test_set_alarm_tool()
    test_list_alarms_tool()
    test_cancel_alarm_tool()
    test_snooze_and_stop_alarm_tools()
    test_alarm_api_registration()
    test_build_alarm_card()
    print("ALL TESTS PASSED!")

