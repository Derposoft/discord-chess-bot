# Hook for pytest package
def pytest_addoption(parser):
    parser.addoption(
        "--file",
        "--config",
        dest="configPath",
        default="./config.json",
        help="File Path to Config File",
    )
