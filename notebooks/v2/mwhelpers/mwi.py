def get_databricks_context():
    from dbruntime.databricks_repl_context import get_context

    return get_context()


def get_user_name():
    return get_databricks_context().user


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


def _parse_matlab_proxy_servers(server_list, debug=False):
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


def get_running_matlab_proxy_servers(debug=False):
    """This function looks at the file system & not the process tree to find the running matlab-proxy servers."""
    printd = _dPrint if debug else lambda x: None

    import glob
    import os
    import sys

    # Add the path to the site_package for matlab-proxy in the container
    matlab_proxy_install_location = _get_matlab_proxy_install_location(debug=debug)
    sys.path.append(matlab_proxy_install_location)

    import matlab_proxy.settings as mwi_settings

    # Find the running servers
    home_folder = mwi_settings.get_mwi_config_folder()

    # Look for files in port folders
    ports_folder = home_folder / "ports"
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
        return _parse_matlab_proxy_servers(running_servers, debug=debug)
    else:
        return ""


def get_toolboxes_available_for_install():
    return ["Symbolic Math", "Deep Learning"]


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


def find_process_using_port(port):
    """Find the process using a specific port.
    Args:
        port (int): The port number to check.
    Returns:
        tuple: A tuple containing the process ID and name if found, else None.
    """
    import psutil

    for proc in psutil.process_iter(["pid", "name", "connections"]):
        for conn in proc.info["connections"]:
            if conn.laddr.port == port:
                return proc.info["pid"], proc.info["name"]
    return None


def stop_matlab_session(session_id):
    import os
    import signal

    process_info = find_process_using_port(int(session_id))
    if process_info:
        pid, pname = process_info
        if "matlab-proxy" in pname:
            print(f"Stopping MATLAB session with ID: {session_id}")
            # Terminate the process
            os.kill(pid, signal.SIGTERM)
    else:
        print(f"No MATLAB session found with ID: {session_id}")


def start_matlab_session(
    configure_psp=False,
    toolboxes_to_install=None,
    debug=False,
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

    print("Starting MATLAB session...")

    port = _find_next_open_port()

    my_env = os.environ
    my_env["MWI_APP_PORT"] = str(port)

    start_msg = f"Starting matlab-proxy-app on port {str(port)}"
    print(start_msg)
    r = subprocess.Popen(["matlab-proxy-app"], env=my_env, close_fds=True)
    print("Started matlab-proxy-app")

    return str(port)


def find_matlab_proxy_app_processes():
    """Find all running MATLAB Proxy App processes."""
    import psutil

    processes = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        for process in proc.info["cmdline"]:
            if "matlab-proxy-app" in process:
                processes.append(proc.info)
    return processes


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
