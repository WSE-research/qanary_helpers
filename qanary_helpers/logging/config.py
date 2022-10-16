mlflow_host = 'localhost'
mlflow_port = 5000
mlflow_port_artifact = None

ssl = False

sftp = False

test_params = ['input', 'true_target', 'predicted_target', 'docker_image_tag', 'runtime']

mlflow_uri = f'http{"s" if ssl else ""}://{mlflow_host}:{mlflow_port}'
