import sys
import pytest
import os

# Define a fixed location for shared data
fixed_earth_data = os.path.join(os.getcwd(), "earth_data_test")

@pytest.fixture(scope="session")
def shared_data_dir():
    # Ensure the directory exists
    os.makedirs(fixed_earth_data, exist_ok=True)
    return fixed_earth_data


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield
