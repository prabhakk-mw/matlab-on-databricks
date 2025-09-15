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
def get_installed_toolboxes(refresh=None):
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
    return "/opt/matlab/R2025a"


def get_matlab_version():
    return "R2025a Update 1 (25.1.0.2973910)"


def get_toolboxes_available_for_install():
    """Get the list of toolboxes available for installation in MATLAB.
    Returns:
        list: List of toolboxes available for installation.
    """
    import requests

    matlab_version = get_matlab_version().split(" ")[
        0
    ]  # Extract the version part, e.g., "R2025a"
    installed_toolboxes = get_installed_toolboxes()
    # Lowercased MATLAB Version
    # Example: R2023a -> r2023a
    matlab_version_lc = matlab_version[0].lower() + matlab_version[1:]

    # URL of the file to download
    url = f"https://raw.githubusercontent.com/mathworks-ref-arch/matlab-dockerfile/refs/heads/main/mpm-input-files/{matlab_version}/mpm_input_{matlab_version_lc}.txt"

    response = requests.get(url)
    if response.status_code != 200:
        return ["Error: Failed to fetch the file content."]

    file_content = response.text

    products = []
    support_packages = []
    optional_features = []

    current_section = None

    for line in file_content.splitlines():
        line = line.strip()
        if line == "## PRODUCTS":
            current_section = "products"
        elif line == "## SUPPORT PACKAGES":
            current_section = "support_packages"
        elif line == "## OPTIONAL FEATURES":
            current_section = "optional_features"
        elif line.startswith("#product."):
            if current_section == "products":
                products.append(line.replace("#product.", "").replace("_", " "))
            elif current_section == "support_packages":
                support_packages.append(line.replace("#product.", "").replace("_", " "))
            elif current_section == "optional_features":
                optional_features.append(
                    line.replace("#product.", "").replace("_", " ")
                )

    # print("Total products found:", len(products))
    # print("Total support_packages found:", len(support_packages))
    # print("Total optional_features found:", len(optional_features))

    # Filter out already installed toolboxes
    toolboxes_available_for_install = [
        toolbox for toolbox in products if toolbox not in installed_toolboxes
    ]

    # Print the extracted lines (optional)
    # print(toolboxes_available_for_install)
    # print("Total toolboxes available for install:", len(toolboxes_available_for_install))
    toolboxes_available_for_install.sort()
    return toolboxes_available_for_install


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
        _call_InstallToolboxes_script(username=None, toolboxes=toolboxes_to_install)

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


def _call_InstallToolboxes_script(username=None, destination=None, toolboxes=None):
    """Creates a user with the given username."""
    import subprocess
    import os

    if username is None:
        print("Installing as root user")

    if destination is None:
        destination = get_matlab_root()

    if toolboxes is None:
        print("No toolboxes to install.")
        return 0
    else:
        print(f"Installing toolboxes: {toolboxes}")
        # Convert the list of toolboxes to a space separated string, where each toolbox name is _ separated.
        products = " ".join(product.replace(" ", "_") for product in toolboxes)

    script_path = os.path.join(
        os.path.dirname(__file__), "scripts", "InstallProducts.sh"
    )
    result = subprocess.run(
        [
            script_path,
            "--destination",
            destination,
            "--release",
            get_matlab_version().split(" ")[0],
            "--products",
            products,
        ],
        capture_output=True,
        text=True,
    )
    script_output = result.stdout
    return script_output
