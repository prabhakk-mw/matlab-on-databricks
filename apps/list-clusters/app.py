from flask import Flask, render_template_string
from databricks.sdk import WorkspaceClient
import os

app = Flask(__name__)


@app.route("/")
def list_clusters():
    # Initialize the Databricks workspace client
    w = WorkspaceClient()

    # Fetch the list of clusters
    clusters = w.clusters.list()

    # Create a simple HTML template to display the clusters
    html_template = """
    <h1>Available Clusters</h1>
    <ul>
    {% for cluster in clusters %}
        <li>{{ cluster.cluster_name }}</li>
    {% endfor %}
    </ul>
    """

    # Render the template with the cluster data
    return render_template_string(html_template, clusters=clusters)

port = os.environ.get("DATABRICKS_APP_PORT","8000")

if __name__ == "__main__":
    app.run(debug=True, port=port)
