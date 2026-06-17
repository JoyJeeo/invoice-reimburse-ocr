import main as app_main


def test_main_entry_exposes_cli_main():
    assert callable(app_main.main)
