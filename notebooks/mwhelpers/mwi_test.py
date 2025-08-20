import random
from time import sleep

# This file list all the APIs and functions that are used by the Notebooks
#   and provides mock implementations which can be used for testing outside of a
#   Databricks environment.


### List of APIs used in the Notebooks ###

## Databricks Related
# get_cluster_name()
# get_databricks_context()
# get_user_name(),

## MATLAB Installation Related
# get_installed_toolboxes()
# get_matlab_root(),
# get_matlab_version(),
# get_toolboxes_available_for_install(),

## MATLAB Proxy Related
# get_running_matlab_proxy_servers(username=get_username())
# get_url_to_matlab(session_id, context)
# start_matlab_session(configure_psp, toolboxes_to_install, username=get_username())
# stop_matlab_session(session, context)


################################################
## Databricks Related APIs
################################################


def get_cluster_name():
    return "Test Cluster"


def get_databricks_context():
    """Get the Databricks context.

    Returns:
        dict: The Databricks context.
    """
    # This is a mock implementation.
    return {
        "cluster_id": "1234",
        "notebook_id": "5678",
        "workspace_url": "https://databricks.com",
    }


def get_user_name():
    return "TestUserName"


################################################
## MATLAB Installation Related
################################################
def get_installed_toolboxes():
    """Get the list of installed toolboxes in MATLAB.

    Returns:
        list: List of installed toolboxes.
    """
    return [
        "MATLAB",
        "Simulink",
        "MATLAB Coder",
    ]


def get_matlab_root():
    return "/opt/matlab/R2023a"


def get_matlab_version():
    return "R2023a"


def get_toolboxes_available_for_install():
    """Get the list of toolboxes available for installation in MATLAB.
    Returns:
        list: List of toolboxes available for installation.
    """
    # This is a mock implementation.
    return ["Symbolic Math", "Deep Learning"]


################################################
## MATLAB Proxy Related
################################################


def get_running_matlab_proxy_servers(username, debug=False, only_ports=True):
    return [str(random.randint(3000, 9999)) for _ in range(3)]


def get_url_to_matlab(session_id, context):
    """Get the URL to a MATLAB session.

    Args:
        session_id (str): The ID of the session.

    Returns:
        str: The URL to the MATLAB session.
    """
    # This is a mock implementation.
    return "https://google.com"
    # return f"http://localhost:8000/matlab/{session_id}"


def start_matlab_session(
    username=None,
    configure_psp=False,
    toolboxes_to_install=None,
):
    """Start a MATLAB session.

    Args:
        configure_psp (bool): Whether to configure the PSP.
        debug (bool): Whether to enable debug mode.

    Returns:
        str: The ID of the started session.
    """

    if configure_psp:
        print("Configuring PSP...")
        # This is a mock implementation.
    if toolboxes_to_install:
        print(f"Installing toolboxes: {toolboxes_to_install}")

    print("Starting MATLAB session...")
    sleep(2)
    # This is a mock implementation.
    return str(random.randint(1000, 9999))


def stop_matlab_session(username, port, context=None):
    """Stop a MATLAB session.

    Args:
        port (str): The port number of the session to stop.
    """
    # This is a mock implementation.
    print(f"Stopping MATLAB session with ID: {port}")
