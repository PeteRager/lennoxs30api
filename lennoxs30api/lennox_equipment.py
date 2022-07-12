class lennox_equipment_diagnostic(object):
    def __init__(self, equipment_id: int, diagnostic_id: int):
        self.equipment_id = equipment_id
        self.diagnostic_id = diagnostic_id
        self.value = None
        self.name: str = None
        self.unit: str = None
        self.valid: bool = True


class lennox_equipment(object):
    def __init__(self, eq_id: int):
        self.equipment_id: int = eq_id
        self.equipType: int = None
        self.equipment_name: str = None
        self.equipment_type_name: str = None
        self.unit_model_number: str = None
        self.unit_serial_number: str = None
        self.diagnostics = {}

    def get_or_create_diagnostic(self, diagnostic_id) -> lennox_equipment_diagnostic:
        if diagnostic_id not in self.diagnostics:
            self.diagnostics[diagnostic_id] = lennox_equipment_diagnostic(
                self.equipment_id, diagnostic_id
            )
        return self.diagnostics[diagnostic_id]
