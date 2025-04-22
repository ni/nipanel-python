import nipanel


def test___streamlit_panel___has_panel_id_and_panel_uri() -> None:
    panel = nipanel.StreamlitPanel("path/to/script")
    assert panel._panel_id is not None
    assert panel._panel_uri == "path/to/script"


def test___two_panels___have_different_panel_ids() -> None:
    panel1 = nipanel.StreamlitPanel("path/to/script1")
    panel2 = nipanel.StreamlitPanel("path/to/script2")
    assert panel1._panel_id != panel2._panel_id


def test___connected_panel___set_value___gets_same_value() -> None:
    panel = nipanel.StreamlitPanel("path/to/script")
    panel.connect()

    panel.set_value("test_id", "test_value")

    # TODO: AB#3095681 - change asserted value to test_value
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()


def test___with_panel___set_value___gets_same_value() -> None:
    with nipanel.StreamlitPanel("path/to/script") as panel:

        panel.set_value("test_id", "test_value")

        # TODO: AB#3095681 - change asserted value to test_value
        assert panel.get_value("test_id") == "placeholder value"
