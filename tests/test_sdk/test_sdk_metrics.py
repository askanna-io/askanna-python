from askanna import track_metric, track_metrics


class TestSDKMetrics:
    def test_track_metric(self):
        track_metric("metricname", "metric_value", "metric_label")

    def test_track_metrics(self):
        track_metrics(metrics={"good": True, "bad": False, "pass": "maybe"}, label={"test": True})

    def test_track_metric_types(self):
        track_metric("metricname_str", "metric_value_string")
        track_metric("metricname_float", 0.005)
        track_metric("metricname_int", 77)
        track_metric("metricname_bool_T", True)
        track_metric("metricname_bool_F", False)
        track_metric("metricname_bool_N", None)
        track_metric("metricname_dict", {"dictkey": "dictvalue"})
