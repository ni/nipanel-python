from nipanel import NiPanel


def test_streamlit_panel() -> None:
    panel = NiPanel.streamlit_panel("path/to/script")
    assert panel.panel_uri == "path/to/script"
    assert panel.panel_id is not None
    panel.connect()
    panel.set_value("test_id", "test_value")
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()


def test_with_streamlit_panel() -> None:
    with NiPanel.streamlit_panel("path/to/script") as panel:
        assert panel.panel_uri == "path/to/script"
        assert panel.panel_id is not None
        panel.set_value("test_id", "test_value")
        assert panel.get_value("test_id") == "placeholder value"
