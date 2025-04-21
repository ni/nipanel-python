from nipanel import NiPanel

def test_streamlit_panel() -> None:
    panel = NiPanel.streamlit_panel("path/to/script")
    assert panel.panel_uri == "path/to/script"
    assert panel.panel_id is not None
    panel.connect() # not implemented, but should not raise an error
    panel.set_value("test_id", "test_value") # not implemented, but should not raise an error
    assert panel.get_value("test_id") == "placeholder value" # not implemented, but should not raise an error
    panel.disconnect() # not implemented, but should not raise an error

def test_with_streamlit_panel() -> None:
    with NiPanel.streamlit_panel("path/to/script") as panel:
        assert panel.panel_uri == "path/to/script"
        assert panel.panel_id is not None
        panel.set_value("test_id", "test_value") # not implemented, but should not raise an error
        assert panel.get_value("test_id") == "placeholder value" # not implemented, but should not raise an error