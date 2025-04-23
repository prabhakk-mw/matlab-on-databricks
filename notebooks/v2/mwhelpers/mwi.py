def dPrint(msg: str):
    import inspect

    caller_info = inspect.stack()[1]
    print(f"{caller_info.function}@{caller_info.lineno}: {msg}")


def get_matlab_proxy_install_location(debug=False):
    printd = dPrint if debug else lambda x: None

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
    raise RuntimeError("No matlab-proxy install location found")


def parse_matlab_proxy_servers(server_list, debug=False):
    printd = dPrint if debug else lambda x: None

    parsed_servers = []
    default_server_address = "http://0.0.0.0:"
    for server in server_list:
        if server.startswith(default_server_address):
            server_info = server[len(default_server_address) :]
            if "/" in server_info:
                port, base_url = server_info.split("/", 1)
            else:
                port, base_url = server_info, ""
            parsed_servers.append({"port": port, "base_url": base_url})
    printd(parsed_servers)

    return parsed_servers


def get_running_matlab_proxy_servers(debug=False):
    printd = dPrint if debug else lambda x: None

    import glob
    import os
    import sys

    # Add the path to the site_package for matlab-proxy in the container
    matlab_proxy_install_location = get_matlab_proxy_install_location(debug=debug)
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
        return parse_matlab_proxy_servers(running_servers, debug=debug)
    else:
        return None


def hello():
    """Prints hello"""
    # Print hello
    return [
        "MATLAB",
        "Simulink",
        "MATLAB Coder",
    ]


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


# from databricks.sdk import WorkspaceClient
# from dbruntime.databricks_repl_context import get_context

# running_servers = get_running_matlab_proxy_servers(debug=False)

# context = get_context()
# cluster_id = context.clusterId
# user_name = context.user

# if context.isInJob:
#     if running_servers:
#         for server in running_servers:
#             print(server)
#         dbutils.notebook.exit(str(running_servers))
#     else:
#         exit_msg="No matlab-proxy servers found. Please start the matlab_proxy first."
#         print(exit_msg)
#         dbutils.notebook.exit(exit_msg)
# else:
#     cluster_name = WorkspaceClient(host=context.browserHostName, token=context.apiToken).clusters.get(context.clusterId).cluster_name

#     workspace_url = f"https://{context.browserHostName}"
#     workspace_id = context.workspaceId

#     cluster_url = f"{workspace_url}/driver-proxy/o/{workspace_id}/{cluster_id}/"
#     template_url = cluster_url + "{{port}}/{{base_url}}/index.html"


#     if running_servers is None:
#         from IPython.display import display, HTML
#         display(HTML("<h3 style='color:red;'>No matlab-proxy servers found. Please start the matlab_proxy first.</h3>"))
#     else:
#         urls = []
#         for server in running_servers:
#             url = template_url
#             for key, value in server.items():
#                 url = url.replace(f"{{{{{key}}}}}", value)
#             urls.append(str(url).rstrip())

#         from IPython.display import display, HTML

#         if urls:
#             html_content = f"<h3 style='color:blue;'>Found the {len(urls)} matlab_proxy server(s) running on cluster: <style='color:red;'>'{cluster_name}'</h3>"
#             html_content += f"<h2 style='color:green;'>Click on the link to access MATLAB:</h2><ul>"
#             for server_number, (url, server) in enumerate(zip(urls, running_servers), start=1):
#                 html_content += f"<h3><li><a href='{url}' target='_blank'>{server_number}. MATLAB running on Port {server['port']}</a></h3></li>"
#             html_content += "</ul>"
#             display(HTML(html_content))
#         else:
#             display(HTML("<h3 style='color:red;'>No matlab-proxy servers found. Please start the matlab_proxy first.</h3>"))
