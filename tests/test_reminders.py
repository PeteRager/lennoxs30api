"""Tests for maintenance reminders"""

from lennoxs30api.s30api_async import lennox_system

from tests.conftest import loadfile


def test_reminders(api_system_04_furn_ac_zoning):
    """Tests loading the reminders"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"
    assert len(system.reminders) == 0

    message = loadfile("reminders.json", "LCC")
    system.processMessage(message)

    assert len(system.reminders) == 8
    reminder = system.reminders[0]
    assert reminder.reminder_id == 0
    assert reminder.kind == "filter1"
    assert reminder.enabled is True
    assert reminder.expiry_type == "systemRunTime"
    assert reminder.reminder_time == 15724800
    assert reminder.viewed is False
    assert reminder.is_valid is True
    assert reminder.expired is False
    assert reminder.expired_time == 0
    assert reminder.expiry_time == 15724800
    assert reminder.set_time == 0
    assert reminder.remaining_pct == 100

    reminder = system.reminders[2]
    assert reminder.kind == "uvBulb"
    assert reminder.enabled is False
    assert reminder.expiry_type == "systemCalendarTime"
    assert reminder.reminder_time is None
    assert reminder.is_valid is True
    assert reminder.expired is False
    assert reminder.expiry_time is None
    assert reminder.remaining_pct is None

    reminder = system.reminders[7]
    assert reminder.kind == "ventilationFilter"
    assert reminder.is_valid is False
    assert reminder.remaining_pct == 0


class CallbackHandler(object):
    """Handler for callbacks"""

    def __init__(self):
        self.called = 0

    def update_callback(self):
        """Callback for changes"""
        self.called = self.called + 1


def test_reminder_update(api_system_04_furn_ac_zoning):
    """Tests incremental updates and subscriptions"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    system.processMessage(loadfile("reminders.json", "LCC"))
    reminder = system.reminders[0]

    callback = CallbackHandler()
    reminder.register_on_update_callback(callback.update_callback, ["remaining_pct", "expired"])
    callback_all = CallbackHandler()
    reminder.register_on_update_callback(callback_all.update_callback)

    # Only the status changes, config is retained
    message = {
        "SenderID": "LCC",
        "MessageType": "PropertyChange",
        "Data": {"reminders": [{"id": 0, "status": {"reminderRemainingPct": 5, "reminderExpiredTime": "123"}}]},
    }
    system.processMessage(message)
    assert reminder.remaining_pct == 5
    assert reminder.expired_time == 123
    assert reminder.kind == "filter1"
    assert reminder.reminder_time == 15724800
    assert callback.called == 1
    assert callback_all.called == 1

    # No change, no callbacks
    system.processMessage(message)
    assert callback.called == 1
    assert callback_all.called == 1

    # Change not in the match list
    message["Data"]["reminders"][0] = {"id": 0, "config": {"viewed": True}}
    system.processMessage(message)
    assert reminder.viewed is True
    assert callback.called == 1
    assert callback_all.called == 2

    message["Data"]["reminders"][0] = {"id": 0, "status": {"reminderExpired": True, "reminderRemainingPct": 0}}
    system.processMessage(message)
    assert reminder.expired is True
    assert reminder.remaining_pct == 0
    assert callback.called == 2
    assert callback_all.called == 3

    # Bad time value
    message["Data"]["reminders"][0] = {"id": 0, "status": {"reminderSetTime": "bogus"}}
    system.processMessage(message)
    assert reminder.set_time is None
