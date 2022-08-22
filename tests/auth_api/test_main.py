from auth_api.main import main


def test_main():
    assert main() == "Hello"
