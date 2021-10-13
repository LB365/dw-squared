

def pytest_addoption(parser):
    parser.addoption("--token", action="store", default="default name")
