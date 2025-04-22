import nipanel


def test___connected_panel___set_value___gets_same_value() -> None:
    panel = nipanel.Panel.streamlit_panel("path/to/script")
    panel.connect()

    panel.set_value("test_id", "test_value")

    # TODO: AB#3095681 - change asserted value to test_value
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()


def test___with_panel___set_value___gets_same_value() -> None:
    with nipanel.Panel.streamlit_panel("path/to/script") as panel:

        panel.set_value("test_id", "test_value")

        # TODO: AB#3095681 - change asserted value to test_value
        assert panel.get_value("test_id") == "placeholder value"
