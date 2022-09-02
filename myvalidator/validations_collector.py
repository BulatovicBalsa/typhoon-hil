import myvalidator.validations as vv


class ValidatorDescription:
    def __init__(self, name, fnc, desc):
        self.name = name
        self.function = fnc
        self.desc = desc


validacije = [
            'default = myvalidator.validations.validate',
            'bus_join = myvalidator.validations:validate_bus_join',
            'known_values = myvalidator.validations:validate_known_values',
            'duplicated_sub_graph = myvalidator.validations:validate_duplicate_sub_graph',
            'value_not_used = myvalidator.validations:validate_calc_value_not_used'
        ]


vd1 = ValidatorDescription('default', vv.run_validations, "run all validations")
vd2 = ValidatorDescription('bus_join', vv.validate_bus_join, "check if two bus joins are directly connected")
vd3 = ValidatorDescription('known_values', vv.validate_known_values, "check if componnents have all known values at "
                                                                     "inputs")
vd4 = ValidatorDescription('duplicated_sub_graph', vv.validate_duplicate_sub_graph, "check if some parts of graphs "
                                                                                    "are similar")
vd5 = ValidatorDescription('value_not_used', vv.validate_calc_value_not_used, "check if graph contains calculations "
                                                                              "that are not used")

validators = {vd1.name: vd1, vd2.name: vd2, vd3.name: vd3, vd4.name: vd4, vd5.name: vd5}


def get_validation_desc(val_name):
    return validators[val_name]


