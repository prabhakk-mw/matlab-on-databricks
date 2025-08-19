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
    return ["Symbolic Math", "Deep Learning", "This FEATURE IS NOT YET IMPLEMENTED"]


################################################
## MATLAB Proxy Related
################################################


def get_running_matlab_proxy_servers(username=None, debug=False, only_ports=True):
    """This function looks at the file system & not the process tree to find the running matlab-proxy servers."""
    printd = _dPrint if debug else lambda x: None

    import glob
    import os
    import sys
    import socket
    import subprocess

    if username is not None:
        hostname = socket.gethostname()
        getent_result = subprocess.run(
            ["getent", "passwd", username], capture_output=True, text=True
        )
        home_folder = (
            getent_result.stdout.strip().split(":")[5]
            + "/.matlab/MWI/hosts/"
            + hostname
        )
        ports_folder = home_folder + "/ports"
    else:
        # Add the path to the site_package for matlab-proxy in the container
        matlab_proxy_install_location = _get_matlab_proxy_install_location(debug=debug)
        sys.path.append(matlab_proxy_install_location)

        import matlab_proxy.settings as mwi_settings

        # Find the running servers
        home_folder = mwi_settings.get_mwi_config_folder()
        ports_folder = home_folder / "ports"

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
        return ""


# [Unused version]
def get_running_matlab_proxy_servers_call_script(username=None, debug=False):
    if username:
        uid = int(
            _call_CreateUser_script(username).splitlines()[1].split(":")[1].strip()
        )
        running_servers = get_output_of_script_as_user(
            command=["matlab-proxy-app-list-servers"], uid=uid
        )
        print(f"Running servers for user {username}: {running_servers}")


def get_url_to_matlab(session_id, context):

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
    configure_psp=False,
    toolboxes_to_install=None,
    username=None,
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
    import subprocess

    port = _find_next_open_port()
    my_env = os.environ
    my_env["MWI_APP_PORT"] = str(port)

    if username is not None:
        uid = int(
            _call_CreateUser_script(username).splitlines()[1].split(":")[1].strip()
        )

        getent_result = subprocess.run(
            ["getent", "passwd", username], capture_output=True, text=True
        )
        my_env["HOME"] = getent_result.stdout.strip().split(":")[5]
        my_env["USER"] = username
        print(f"Starting MATLAB session as user: {username} & uid: {uid}")
        # Run the command as the specified user
        run_as_user(command=["matlab-proxy-app"], uid=uid, env=my_env)
    else:
        print("Starting MATLAB session as root user")
        # Run the command as the root user
        print("Starting MATLAB session...")

        start_msg = f"Starting matlab-proxy-app on port {str(port)}"
        print(start_msg)
        r = subprocess.Popen(["matlab-proxy-app"], env=my_env, close_fds=True)
        print("Started matlab-proxy-app")

    return str(port)


def stop_matlab_session(username, port, context=None):
    if context and context.isInJob:
        print("Running inside a job, aborting...")
        return
    if port or username is None:
        print("No username or port provided, aborting...")
        return

    server = get_running_matlab_proxy_servers(username=username, only_ports=False)
    # Get the server URL for the given port
    if server is None:
        print(f"No servers found for {username}, aborting...")
        return
    server_url = server[str(port)]

    # Find the URL to the session
    if server_url is None:
        print("No server found for the given port, aborting...")
        return

    # Send a DELETE request to the SHUTDOWN_INTEGRATION endpoint
    # mwi.send_http_request("http://0.0.0.0:3001/matlab/shutdown_integration","DELETE")
    shutdown_url = server_url + "/shutdown_integration"
    print(f"Stopping MATLAB session with ID: {port}")
    print(f"Sending shutdown request to URL: {shutdown_url}")

    send_http_request(shutdown_url, method="DELETE")

    # Send the shutdown request using OS.KILL (Not a good idea, as clean up is not guaranteed.)
    # import os
    # import signal
    # process_info = find_process_using_port(int(port))
    # if process_info:
    #     pid, pname = process_info
    #     if "matlab-proxy" in pname:
    #         print(f"Stopping MATLAB session with ID: {port}")
    #         # Terminate the process
    #         os.kill(pid, signal.SIGTERM)
    # else:
    #     print(f"No MATLAB session found with ID: {port}")


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


################################################
## Helper Functions
################################################
def _dPrint(msg: str):
    import inspect

    caller_info = inspect.stack()[1]
    print(f"{caller_info.function}@{caller_info.lineno}: {msg}")


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


def _parse_matlab_proxy_servers(server_list, debug=False) -> dict:
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
    if not hasattr(_call_ListInstalledProducts_script, "_cached_output"):
        _call_ListInstalledProducts_script._cached_output = (
            _call_ListInstalledProducts_script()
        )

    return _call_ListInstalledProducts_script._cached_output


def send_http_request(url, method="GET", data=None):
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


def _call_CreateUser_script(username=None):
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
    import os
    import subprocess

    def demote():
        os.setuid(uid)

    process = subprocess.Popen(command, env=env, preexec_fn=demote)
    return process


def get_output_of_script_as_user(uid, command=None, env=None):
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
    import socket

    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt
        result = sock.connect_ex((host, port))
        if result != 0:  # 0 means the port is open
            sock.close()
            return port

    return None
