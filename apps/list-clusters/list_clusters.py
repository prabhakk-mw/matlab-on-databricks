from databricks.sdk import WorkspaceClient


def list_clusters():
    # Initialize the Databricks workspace client
    w = WorkspaceClient()

    # Fetch the list of clusters
    clusters = w.clusters.list()

    # Print the cluster names
    print("Available Clusters:")
    for cluster in clusters:
        print(f"- {cluster.cluster_name}")


if __name__ == "__main__":
    list_clusters()
