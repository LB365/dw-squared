
def pytest_addoption(parser):
    parser.addoption("--mapping", action="store", default="default name")
    parser.addoption("--endpoint", action="store", default="default name")
    parser.addoption("--token", action="store", default="default name")