from .s30exception import EC_BAD_PARAMETERS, S30Exception


class lennox_equipment_diagnostic(object):
    def __init__(self, equipment_id: int, diagnostic_id: int):
        self.equipment_id = equipment_id
        self.diagnostic_id = diagnostic_id
        self.value = None
        self.name: str = None
        self.unit: str = None
        self.valid: bool = True


LENNOX_EQUIPMENT_PARAMETER_FORMAT_RANGE = "range"
LENNOX_EQUIPMENT_PARAMETER_FORMAT_RADIO = "radio"


class lennox_equipment_parameter(object):
    def __init__(self, equipment_id: int, pid: int):
        self.name: str = None
        self.equipment_id = equipment_id
        self.pid: int = pid
        self.defaultValue: str = None
        self.descriptor: str = None
        self.enabled: bool = None
        self.format: str = None
        self.value: str = None
        self.radio: dict[int, str] = {}
        self.range_min: str = None
        self.range_max: str = None
        self.range_inc: str = None
        self.string_max: str = None
        self.unit: str = None

    def fromJson(self, js: dict):
        self.defaultValue = js.get("defaultValue", self.defaultValue)
        self.descriptor = js.get("descriptor", self.descriptor)
        self.enabled = js.get("enabled", self.enabled)
        self.format = js.get("format", self.format)
        self.name = js.get("name", self.name)
        self.pid = js.get("pid", self.pid)
        self.value = js.get("value", self.value)
        self.unit = js.get("unit", self.unit)
        if "radio" in js:
            if "texts" in js["radio"]:
                for text in js["radio"]["texts"]:
                    if "id" in text and "text" in text:
                        self.radio[text["id"]] = text["text"]
        if "range" in js:
            self.range_min = js["range"].get("min", self.range_min)
            self.range_max = js["range"].get("max", self.range_max)
            self.range_inc = js["range"].get("inc", self.range_inc)

        if "string" in js:
            self.string_max = js["string"].get("max", self.string_max)

    def validate_and_translate(self, value: str) -> str:
        if self.descriptor == LENNOX_EQUIPMENT_PARAMETER_FORMAT_RADIO:
            for k, v in self.radio.items():
                if v == value:
                    return k
            raise S30Exception(
                f"lennox_equipment_parameter invalid radio value provided [{value}] pid [{self.pid}] name [{self.name}] radio_value [{self.radio.values()}]",
                EC_BAD_PARAMETERS,
                1,
            )
        if self.descriptor == LENNOX_EQUIPMENT_PARAMETER_FORMAT_RANGE:
            try:
                f_val = float(value)
                f_min = float(self.range_min)
                f_max = float(self.range_max)
                f_inc = float(self.range_inc)
                if f_val < f_min or f_val > f_max:
                    raise S30Exception(
                        f"lennox_equipment_parameter invalid value provided [{value}] must be between [{self.range_min}] and [{self.range_max}] pid [{self.pid}] name [{self.name}]",
                        EC_BAD_PARAMETERS,
                        2,
                    )
                if f_val % f_inc != 0:
                    raise S30Exception(
                        f"lennox_equipment_parameter invalid value provided [{value}] must a multiple of [{self.range_inc}] pid [{self.pid}] name [{self.name}] radio_value [{self.radio.values}]",
                        EC_BAD_PARAMETERS,
                        3,
                    )
                return value
            except Exception as e:
                raise S30Exception(
                    f"lennox_equipment_parameter invalid value or limits [{value}] range_inc [{self.range_inc}] range_min [{self.range_min}] range_max [{self.range_max}] pid [{self.pid}] name [{self.name}] error [{e}]",
                    EC_BAD_PARAMETERS,
                    4,
                )
        raise S30Exception(
            f"lennox_equipment_parameter unsupported descriptor [{self.descriptor}] pid [{self.pid}] name [{self.name} - please raise an issue",
            EC_BAD_PARAMETERS,
            5,
        )


class lennox_equipment(object):
    def __init__(self, eq_id: int):
        self.equipment_id: int = eq_id
        self.equipType: int = None
        self.equipment_name: str = None
        self.equipment_type_name: str = None
        self.unit_model_number: str = None
        self.unit_serial_number: str = None
        self.diagnostics: dict[int, lennox_equipment_diagnostic] = {}
        self.parameters: dict[int, lennox_equipment_parameter] = {}

    def get_or_create_diagnostic(self, diagnostic_id) -> lennox_equipment_diagnostic:
        if diagnostic_id not in self.diagnostics:
            self.diagnostics[diagnostic_id] = lennox_equipment_diagnostic(
                self.equipment_id, diagnostic_id
            )
        return self.diagnostics[diagnostic_id]

    def get_or_create_parameter(self, pid) -> lennox_equipment_parameter:
        if pid not in self.parameters:
            self.parameters[pid] = lennox_equipment_parameter(self.equipment_id, pid)
        return self.parameters[pid]
