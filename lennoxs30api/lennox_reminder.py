# pylint: disable=invalid-name
"""Maintenance reminders (filters, UV bulb, humidifier pad, etc.)"""

from .subscriber_base import SubscriberBase


def _to_int(value):
    """Lennox sends the reminder times as strings"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class LennoxReminder(SubscriberBase):
    """Represents a maintenance reminder"""

    def __init__(self, reminder_id: int):
        SubscriberBase.__init__(self)
        self.reminder_id: int = reminder_id
        # Config
        self.kind: str = None
        self.enabled: bool = None
        self.expiry_type: str = None
        self.reminder_time: int = None
        self.viewed: bool = None
        # Status
        self.is_valid: bool = None
        self.expired: bool = None
        self.expired_time: int = None
        self.expiry_time: int = None
        self.set_time: int = None
        self.remaining_pct: int = None

    def debug_string(self) -> str:
        return f"reminder id [{self.reminder_id}] kind [{self.kind}]"

    def update_from_json(self, reminder: dict):
        """Updates the object from JSON"""
        if "config" in reminder:
            config = reminder["config"]
            self.attr_updater(config, "kind")
            self.attr_updater(config, "enabled")
            self.attr_updater(config, "reminderExpiryType", "expiry_type")
            self.attr_updater(config, "reminderTime", "reminder_time")
            self.attr_updater(config, "viewed")
        if "status" in reminder:
            status = dict(reminder["status"])
            for key in ("reminderExpiredTime", "reminderExpiryTime", "reminderSetTime"):
                if key in status:
                    status[key] = _to_int(status[key])
            self.attr_updater(status, "isValid", "is_valid")
            self.attr_updater(status, "reminderExpired", "expired")
            self.attr_updater(status, "reminderExpiredTime", "expired_time")
            self.attr_updater(status, "reminderExpiryTime", "expiry_time")
            self.attr_updater(status, "reminderSetTime", "set_time")
            self.attr_updater(status, "reminderRemainingPct", "remaining_pct")
        self.execute_on_update_callbacks()
