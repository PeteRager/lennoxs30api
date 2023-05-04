"""Tests the equipment response"""
# pylint: disable=line-too-long
# pylint: disable=protected-access
# pylint: disable=protected-access
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from lennoxs30api.lennox_equipment import lennox_equipment
from lennoxs30api.s30api_async import (
    LENNOX_EQUIPMENT_TYPE_AIR_HANDLER,
    LENNOX_EQUIPMENT_TYPE_HEAT_PUMP,
    s30api_async,
    lennox_system,
    LENNOX_EQUIPMENT_TYPE_SUBNET_CONTROLLER,
    LENNOX_EQUIPMENT_TYPE_AIR_CONDITIONER,
    LENNOX_EQUIPMENT_TYPE_FURNACE,
    LENNOX_EQUIPMENT_TYPE_ZONING_CONTROLLER,
)

from tests.conftest import loadfile


def setup_load_lcc_configuration() -> s30api_async:
    api = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api.setup_local_homes()
    return api


def test_process_splitsetpoint():
    api = setup_load_lcc_configuration()
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "LCC"

    data = loadfile("equipments_lcc_singlesetpoint.json")
    api.processMessage(data)

    assert lsystem.single_setpoint_mode is True

    data = loadfile("equipments_lcc_splitsetpoint.json")
    api.processMessage(data)

    assert lsystem.single_setpoint_mode is False


def test_process_equipments_ac_furnace_zoning(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    assert len(system.equipment) == 4

    eq: lennox_equipment = system.equipment[0]
    assert eq.equipment_id == 0
    assert eq.equipment_name == "Subnet controller"
    assert eq.equipment_type_name == "System"
    assert eq.unit_model_number == "105081-07"
    assert eq.unit_serial_number == "KL20H56000"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_SUBNET_CONTROLLER
    eq: lennox_equipment = system.equipment[1]
    assert eq.equipment_id == 1
    assert eq.equipment_name == "Outdoor Unit"
    assert eq.equipment_type_name == "Air Conditioner"
    assert eq.unit_model_number == "EL18XCVS036-230A01"
    assert eq.unit_serial_number == "5821E06000"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_AIR_CONDITIONER
    eq: lennox_equipment = system.equipment[2]
    assert eq.equipment_id == 2
    assert eq.equipment_name == "Furnace"
    assert eq.equipment_type_name == "Furnace"
    assert eq.unit_model_number == "SLP99UH110XV60C-01"
    assert eq.unit_serial_number == "5920H11000"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_FURNACE
    eq: lennox_equipment = system.equipment[3]
    assert eq.equipment_id == 3
    assert eq.equipment_name == "Zoning Controller (zone 1 to 4)"
    assert eq.equipment_type_name == "Zoning Controller (zone 1 to 4)"
    assert eq.unit_model_number == "103916-03"
    assert eq.unit_serial_number == "BT21B13000"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_ZONING_CONTROLLER

    assert system.has_indoor_unit is True
    assert system.has_outdoor_unit is True
    assert system.indoorUnitType.casefold() == system.equipment[2].equipment_type_name.casefold()
    assert system.outdoorUnitType.casefold() == system.equipment[1].equipment_type_name.casefold()

    eq = system.get_indoor_unit_equipment()
    assert eq.equipment_id == 2

    system.indoorUnitType = None
    eq = system.get_indoor_unit_equipment()
    assert eq is None
    system.indoorUnitType = "mangled"
    eq = system.get_indoor_unit_equipment()
    assert eq.equipment_id == 2

    eq = system.get_outdoor_unit_equipment()
    assert eq.equipment_id == 1
    system.outdoorUnitType = None
    eq = system.get_outdoor_unit_equipment()
    assert eq is None
    system.outdoorUnitType = "mangled"
    eq = system.get_outdoor_unit_equipment()
    assert eq.equipment_id == 1


def test_process_equipments_HeatPump_AirHandler():
    api = setup_load_lcc_configuration()
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"
    assert len(system.equipment) == 0

    data = loadfile("equipments_lcc_singlesetpoint.json")
    api.processMessage(data)

    assert len(system.equipment) == 3

    eq: lennox_equipment = system.equipment[0]
    assert eq.equipment_name == "Subnet Controller"
    assert eq.equipment_type_name == "System"
    assert eq.unit_model_number == "105081-07"
    assert eq.unit_serial_number == "KL21D01999"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_SUBNET_CONTROLLER
    eq: lennox_equipment = system.equipment[1]
    assert eq.equipment_id == 1
    assert eq.equipment_name == "Outdoor Unit"
    assert eq.equipment_type_name == "Heat Pump"
    assert eq.unit_model_number == "XP20-036-230B04"
    assert eq.unit_serial_number == "5821D09999"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_HEAT_PUMP
    eq: lennox_equipment = system.equipment[2]
    assert eq.equipment_id == 2
    assert eq.equipment_name == "Air Handler"
    assert eq.equipment_type_name == "Air Handler"
    assert eq.unit_model_number == "CBA38MV-036-230-02"
    assert eq.unit_serial_number == "1621B25999"
    assert eq.equipType == LENNOX_EQUIPMENT_TYPE_AIR_HANDLER
