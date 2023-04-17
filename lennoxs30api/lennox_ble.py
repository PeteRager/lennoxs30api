# pylint: disable=invalid-name
"""Bluetooth Sensors"""
from .subscriber_base import SubscriberBase


class LennoxBleInput(SubscriberBase):
    """Represents a BLE sensor value"""

    def __init__(self, ble_id: int, input_id: int):
        SubscriberBase.__init__(self)
        self.ble_id = ble_id
        self.input_id = input_id
        self.value = None
        self.name: str = None
        self.unit: str = None

    def update_from_json(self, status: dict):
        """Updates the object from JSON"""
        self.attr_updater(status, "name")
        self.attr_updater(status, "unit")
        if "values" in status:
            self.attr_updater(status["values"][0], "value")
        self.execute_on_update_callbacks()

    def debug_string(self) -> str:
        return f"ble id [{self.ble_id}] input_id [{self.input_id}]"


class LennoxBle(SubscriberBase):
    """Represent a BLE device"""

    def __init__(self, ble_id: int):
        SubscriberBase.__init__(self)
        self.ble_id: int = ble_id
        self.deviceType: str = None
        self.deviceName: str = None
        self.controlModelNumber: str = None
        self.controlSerialNumber: str = None
        self.controlHardwareVersion: str = None
        self.controlSoftwareVersion: str = None
        self.commStatus: str = None

        self.inputs: dict[int, LennoxBleInput] = {}

    def debug_string(self) -> str:
        return f"ble id [{self.ble_id}]"

    def get_or_create_ble_input(self, input_id) -> LennoxBleInput:
        """Returns exsting BLE device or creates and returns a new one"""
        if input_id not in self.inputs:
            self.inputs[input_id] = LennoxBleInput(self.ble_id, input_id)
        return self.inputs[input_id]

    def update_from_json(self, device: dict):
        """Updates the object from JSON"""
        self.attr_updater(device, "deviceType")
        self.attr_updater(device, "deviceName")
        self.attr_updater(device, "deviceType")
        if "devStatus" in device and "commStatus" in device["devStatus"]:
            devStatus = device["devStatus"]
            self.attr_updater(devStatus, "commStatus")
            for t_status in devStatus.get("inputsStatus", []):
                if "status" in t_status:
                    status = t_status["status"]
                    if "vid" in status and status["vid"] != 0:
                        input_sensor = self.get_or_create_ble_input(status["vid"])
                        input_sensor.update_from_json(status)

        for feature in device.get("config", {}).get("features", []):
            fid = feature.get("feature", {}).get("fid")
            val0 = feature["feature"]["values"][0]
            match fid:
                case 3000:
                    self.attr_updater(val0, "value", "controlModelNumber")
                case 3001:
                    self.attr_updater(val0, "value", "controlSerialNumber")
                case 3002:
                    self.attr_updater(val0, "value", "controlHardwareVersion")
                case 3003:
                    self.attr_updater(val0, "value", "controlSoftwareVersion")
