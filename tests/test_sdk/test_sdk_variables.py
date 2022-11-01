from askanna import track_variable, track_variables


class TestSDKVariables:
    def test_track_variable(self):
        track_variable("variablename", "variable_value", "variable_label")

    def test_track_variables(self):
        track_variables(
            variables={"good": True, "bad": False, "pass": "maybe"},
            label={"test": True},
        )

    def test_track_variable_types(self):
        track_variable("variablename_str", "variable_value_string")
        track_variable("variablename_float", 0.005)
        track_variable("variablename_int", 77)
        track_variable("variablename_bool_T", True)
        track_variable("variablename_bool_F", False)
        track_variable("variablename_bool_N", None)
        track_variable("variablename_dict", {"dictkey": "dictvalue"})
