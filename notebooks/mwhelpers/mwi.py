# Copyright 2025 The MathWorks, Inc.
## This module hosts function related to using MATLAB Proxy on Databricks.

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
    from databricks.sdk import WorkspaceClient

    context = get_databricks_context()
    if context.isInJob:
        return "Job Cluster"
    else:
        cluster_name = (
            WorkspaceClient(host=context.browserHostName, token=context.apiToken)
            .clusters.get(context.clusterId)
            .cluster_name
        )
        return cluster_name


def get_databricks_context():
    from dbruntime.databricks_repl_context import get_context

    return get_context()


def get_user_name():
    # If username contains and email address, remove the domain part
    # and return only the username
    # Example: "prabhakk@mw.com" -> "prabhakk"
    username = get_databricks_context().user
    if "@" in username:
        username = username.split("@")[0]
    return username


################################################
## MATLAB Installation Related
################################################

def get_installed_toolboxes():
    """Get the list of installed toolboxes in MATLAB.

    Returns:
        list: List of installed toolboxes.
    """

    installed_products = _call_ListInstalledProducts_script_cached()
    return installed_products.splitlines()[4:]


def get_matlab_root():
    """Get the root directory of MATLAB.

    Returns:
        str: The root directory of MATLAB.
    """
    import subprocess

    result = subprocess.run(["which", "matlab"], capture_output=True, text=True)
    matlab_path = result.stdout.strip()

    resolved_path = subprocess.run(
        ["readlink", "-f", matlab_path], capture_output=True, text=True
    ).stdout.strip()
    if resolved_path.endswith("/bin/matlab"):
        resolved_path = resolved_path.replace("/bin/matlab", "")

    return resolved_path


def get_matlab_version():
    """Get the version of MATLAB.

    Returns:
        str: The version of MATLAB.
    """
    return (
        _call_ListInstalledProducts_script_cached()
        .splitlines()[2]
        .split(":")[1]
        .strip()
    )


def get_toolboxes_available_for_install():
    import requests

    matlab_version = get_matlab_version().split(" ")[0]  # Extract the version part, e.g., "R2025a"
    installed_toolboxes = get_installed_toolboxes()
    # Lowercased MATLAB Version
    # Example: R2023a -> r2023a
    matlab_version_lc = matlab_version[0].lower() + matlab_version[1:]

    # URL of the file to download
    url = f"https://raw.githubusercontent.com/mathworks-ref-arch/matlab-dockerfile/refs/heads/main/mpm-input-files/{matlab_version}/mpm_input_{matlab_version_lc}.txt"

    response = requests.get(url)
    if response.status_code != 200:
        return["Error: Failed to fetch the file content."]
        

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
                # print(".")
                products.append(line.replace("#product.", "").replace("_", " "))
            elif current_section == "support_packages":
                # print("*")
                support_packages.append(line.replace("#product.", "").replace("_", " "))
            elif current_section == "optional_features":
                # print(f"Adding optional feature: {line}")
                optional_features.append(line.replace("#product.", "").replace("_", " "))


    # print("Total products found:", len(products))
    # print("Total support_packages found:", len(support_packages))
    # print("Total optional_features found:", len(optional_features))

    # Filter out already installed toolboxes
    toolboxes_available_for_install = [
        toolbox for toolbox in products if toolbox not in installed_toolboxes]
    
    # Print the extracted lines (optional)
    # print(toolboxes_available_for_install)
    # print("Total toolboxes available for install:", len(toolboxes_available_for_install))
    toolboxes_available_for_install.sort()
    return toolboxes_available_for_install


################################################
## MATLAB Proxy Related
################################################

def get_running_matlab_proxy_servers(username, debug=False, only_ports=True):
    """This function looks at the file system & not the process tree to find the running matlab-proxy servers."""
    printd = _dPrint if debug else lambda x: None

    import glob
    import os
    import socket

    if username is None:
        return []

    home_folder = _get_home_folder(username)
    if not home_folder:
        #  User does not exist, this function does not create the user.
        return []

    hostname = socket.gethostname()
    ports_folder = home_folder + "/.matlab/MWI/hosts/" + hostname + "/ports"

    # Look for files in port folders
    search_string = str(ports_folder) + "/**/mwi_server.info"

    search_results = sorted(glob.glob(search_string), key=os.path.getmtime)
    running_servers = []
    for server in search_results:
        with open(server) as f:
            server_info = f.read()
            printd(str(server_info))
            running_servers.append(str(server_info).rstrip())

    # return running_servers
    if running_servers:
        server_dict = _parse_matlab_proxy_servers(running_servers, debug=debug)
        return list(server_dict.keys()) if only_ports else server_dict
    else:
        return []


def get_url_to_matlab(session_id, context):
    """Get the Driver Proxy URL to the MATLAB session."""
    if context.isInJob:
        print("Running inside a job, aborting...")
        return None
    else:

        workspace_url = f"https://{context.browserHostName}"
        workspace_id = context.workspaceId
        cluster_id = context.clusterId

        cluster_url = f"{workspace_url}/driver-proxy/o/{workspace_id}/{cluster_id}/"
        template_url = cluster_url + "{{port}}/{{base_url}}/index.html"

        assumed_base_url = "matlab"
        url = template_url.replace("{{port}}", str(session_id)).replace(
            "{{base_url}}", assumed_base_url
        )
        return url


def start_matlab_session(
    username=None,
    configure_psp=False,
    toolboxes_to_install=None,
):
    """Start a MATLAB session.

    Args:
        configure_psp (bool): Whether to configure the MATLAB Proxy Server.
        toolboxes_to_install (list): List of toolboxes to install.
        debug (bool): Whether to enable debug mode.

    Returns:
        str: The ID of the started MATLAB session.
    """
    import os

    if username is None:
        print("No username provided, aborting...")
        return ""

    if configure_psp:
        print("Configuring PSP...")
        # This is a mock implementation.
    if toolboxes_to_install:
        print(f"Installing toolboxes: {toolboxes_to_install}")
        _call_InstallToolboxes_script(username=None, toolboxes=toolboxes_to_install)

    home_folder = _get_home_folder(username)
    if not home_folder:
        print(f"User {username} does not exist, creating user...")
        # Create the user if it does not exist
        uid = _create_user(username)
        print(f"User {username} created with UID: {uid}")
        home_folder = _get_home_folder(username)

    if not home_folder:
        print("Unable to find the home folder, aborting...")
        return ""

    uid = _get_uid(username)
    if not uid:
        print(f"Failed to create user {username}, aborting...")
        return ""

    port = _find_next_open_port()
    if port is None:
        print("No ports available, aborting...")
        return ""

    env_vars = os.environ
    env_vars["HOME"] = home_folder
    env_vars["USER"] = username
    env_vars["MWI_APP_PORT"] = str(port)
    print(f"Starting MATLAB session as user: {username} & uid: {uid}")
    # Run the command as the specified user
    run_as_user(command=["matlab-proxy-app"], uid=uid, env=env_vars)
    print(f"Started matlab-proxy-app on port: {port}")

    return str(port)


def stop_matlab_session(username, port, context=None):
    """Stop a MATLAB session running for the specified user and port."""
    if context and context.isInJob:
        print("Running inside a job, aborting...")
        return False
    if port is None:
        print("No port provided, aborting...")
        return False
    if username is None:
        print("No username provided, aborting...")
        return False

    server = get_running_matlab_proxy_servers(username=username, only_ports=False)
    # Get the server URL for the given port
    if server is None:
        print(f"No servers found for {username}, aborting...")
        return False
    server_url = server[str(port)]

    # Find the URL to the session
    if server_url is None:
        print("No server found for the given port, aborting...")
        return False

    # Send a DELETE request to the SHUTDOWN_INTEGRATION endpoint
    shutdown_url = server_url + "/shutdown_integration"
    print(f"Stopping MATLAB session with ID: {port}")
    print(f"Sending shutdown request to URL: {shutdown_url}")

    send_http_request(shutdown_url, method="DELETE")

    # Send the shutdown request using OS.KILL (Not a good idea, as clean up is not guaranteed.)



################################################
## Helper Functions
################################################
def _dPrint(msg: str):
    import inspect

    caller_info = inspect.stack()[1]
    print(f"{caller_info.function}@{caller_info.lineno}: {msg}")


def _query_system_for_user(username):
    """Query the system for the user in the Name Service Switch Library PASSWD."""
    "Returns empty string if the user is not found."
    import subprocess

    if username is None:
        return ""

    getent_result = subprocess.run(
        ["getent", "passwd", username], capture_output=True, text=True
    )
    if getent_result.returncode != 0:
        return ""
    
    return getent_result


def _get_home_folder(username):
    """Get the home folder for the provided username, if user exists."""
    getent_result = _query_system_for_user(username)
    if getent_result:
        home_folder = getent_result.stdout.strip().split(":")[5]
        return home_folder
    return ""


def _get_uid(username):
    """Get the UID of the user."""
    getent_result = _query_system_for_user(username)
    if getent_result:
        uid = int(getent_result.stdout.strip().split(":")[2])
        return uid
    return None


def _create_user(username):
    """Create a user with the given username."""
    """ If the user already exists, it returns the UID of the user."""
    if username is None:
        return ""

    create_user_result = _call_CreateUser_script(username)
    if create_user_result:
        # Return the UID
        return create_user_result.splitlines()[1].split(":")[1].strip()
    else:
        print(f"Failed to create user: {username}")
        return ""


def _parse_matlab_proxy_servers(server_list, debug=False) -> dict:
    """Returns a dictionary of server ports and their URLs."""
    printd = _dPrint if debug else lambda x: None

    parsed_servers = {}
    default_server_address = "http://0.0.0.0:"
    for server in server_list:
        if server.startswith(default_server_address):
            server_info = server[len(default_server_address) :]
            if "/" in server_info:
                port, base_url = server_info.split("/", 1)
            else:
                port, base_url = server_info, ""
            parsed_servers[str(port)] = server
    printd(parsed_servers)

    return parsed_servers


def _call_ListInstalledProducts_script():
    """Call the ListInstalledProducts.sh script to get the list of installed products."""
    """This function is used to get the list of installed products in MATLAB, excluding Support Packages."""
    import subprocess
    import os

    script_path = os.path.join(
        os.path.dirname(__file__), "scripts", "ListInstalledProducts.sh"
    )
    result = subprocess.run(
        [
            script_path,
            "-r",
            get_matlab_root(),
        ],
        capture_output=True,
        text=True,
    )
    script_output = result.stdout
    return script_output


def _call_ListInstalledProducts_script_cached():
    """ Listing all products can be time consuming, so we cache the output."""
    if not hasattr(_call_ListInstalledProducts_script, "_cached_output"):
        _call_ListInstalledProducts_script._cached_output = (
            _call_ListInstalledProducts_script()
        )

    return _call_ListInstalledProducts_script._cached_output


def send_http_request(url, method="GET", data=None):
    """Send an HTTP request to the specified URL."""
    import requests

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, data=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError("Unsupported HTTP method: {}".format(method))

        return response
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None


def _call_InstallToolboxes_script(username=None, destination=None, toolboxes=None):
    """Installs provided toolboxes. (SupportPackages are not yet supported.)"""
    import subprocess
    import os

    if username is None:
        print("Installing as root user")

    if destination is None:
        destination = get_matlab_root()

    if toolboxes is None:
        print('No toolboxes to install.')
        return 0
    else:
        print(f"Installing toolboxes: {toolboxes}")
        # Convert the list of toolboxes to a space separated string, where each toolbox name is _ separated.
        products = " ".join(product.replace(" ", "_") for product in toolboxes)

    script_path = os.path.join(os.path.dirname(__file__), "scripts", "InstallProducts.sh")
    print("Installation has begun...")
    result = subprocess.run(
        [
            script_path,
            "--destination",
            destination,
            "--release",
            get_matlab_version().split(" ")[0],
            "--products",
            products
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error installing toolboxes: {result.stderr}")
        return None
    print("Installation completed successfully.")
    script_output = result.stdout
    return script_output


def _call_CreateUser_script(username=None):
    """Creates a user with the given username."""
    import subprocess
    import os

    if username is None:
        return None

    script_path = os.path.join(os.path.dirname(__file__), "scripts", "CreateUser.sh")
    result = subprocess.run(
        [
            script_path,
            "-u",
            username,
        ],
        capture_output=True,
        text=True,
    )
    script_output = result.stdout
    return script_output


def run_as_user(uid, command=None, env=None):
    """Run a command as a specific user."""
    import os
    import subprocess

    def demote():
        os.setuid(uid)

    process = subprocess.Popen(command, env=env, preexec_fn=demote)
    return process


def get_output_of_script_as_user(uid, command=None, env=None):
    """Run a command as a specific user and return the output."""
    import os
    import subprocess

    def demote():
        os.setuid(uid)

    output = subprocess.run(
        command, env=env, preexec_fn=demote, capture_output=True, text=True
    )
    if output.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error message: {output.stderr}")
        return None
    else:
        print(f"Command output: {output.stdout}")
        print(f"Command error: {output.stderr}")
        print(f"Command return code: {output.returncode}")
    return output.stdout


def _find_next_open_port(
    *, host="0.0.0.0", start_port: int = 3000, end_port: int = 9999
):
    """Find the next open port in the specified range."""
    """Databricks only proxies ports in the range 3000-9999."""
    import socket

    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt
        result = sock.connect_ex((host, port))
        if result != 0:  # 0 means the port is open
            sock.close()
            return port

    return None


def _get_matlab_proxy_install_location(debug=False):
    printd = _dPrint if debug else lambda x: None

    import subprocess

    result = subprocess.run(
        ["/usr/bin/python3", "-m", "pip", "show", "matlab-proxy"],
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Location:"):
            matlab_proxy_install_location = line.split(" ")[1]
            printd(matlab_proxy_install_location)

            return matlab_proxy_install_location
    printd("No matlab-proxy install location found")
    return None


def _parse_matlab_proxy_server_ports(server_list, debug=False):
    printd = _dPrint if debug else lambda x: None

    parsed_servers = []
    default_server_address = "http://0.0.0.0:"
    for server in server_list:
        if server.startswith(default_server_address):
            server_info = server[len(default_server_address) :]
            if "/" in server_info:
                port, base_url = server_info.split("/", 1)
            else:
                port, base_url = server_info, ""
            # parsed_servers.append({"port": port, "base_url": base_url})
            parsed_servers.append(str(port))
    printd(parsed_servers)

    return parsed_servers


# def find_pid():
#     import psutil
#     for process in psutil.process_iter(['pid', 'name']):
#         try:
#             connections = process.net_connections()
#             if connections:
#                 print(f"Process: {process.info['name']} (PID: {process.info['pid']})")
#                 for conn in connections:
#                     print(f"  - {conn}")
#         except psutil.Error as e:
#             print(f"Error accessing process {process.info['pid']}: {e}")

# def find_process_using_port(port):
#     """Find the process using a specific port.
#     Args:
#         port (int): The port number to check.
#     Returns:
#         tuple: A tuple containing the process ID and name if found, else None.
#     """
#     import psutil

#     for proc in psutil.process_iter(["pid", "name", "connections"]):
#         for conn in proc.info["connections"]:
#             if conn.laddr.port == port:
#                 return proc.info["pid"], proc.info["name"]
#     return None

# def stop_matlab_session_old(session_id):
#     import os
#     import signal

#     process_info = find_process_using_port(int(session_id))
#     if process_info:
#         pid, pname = process_info
#         if "matlab-proxy" in pname:
#             print(f"Stopping MATLAB session with ID: {session_id}")
#             # Terminate the process
#             os.kill(pid, signal.SIGTERM)
#     else:
#         print(f"No MATLAB session found with ID: {session_id}")


# def get_running_matlab_proxy_servers_call_script(username=None, debug=False):
#     if username:
#         uid = int(
#             _call_CreateUser_script(username).splitlines()[1].split(":")[1].strip()
#         )
#         running_servers = get_output_of_script_as_user(
#             command=["matlab-proxy-app-list-servers"], uid=uid
#         )
#         print(f"Running servers for user {username}: {running_servers}")