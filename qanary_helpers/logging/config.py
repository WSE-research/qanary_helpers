mlflow_host = 'localhost'
mlflow_port = 5000
mlflow_port_artifact = None

ssl = False

sftp = False

test_params = ['input', 'model_uuid', 'runtime']
test_dicts = ['true_target', 'predicted_target']

mlflow_uri = f'http{"s" if ssl else ""}://{mlflow_host}:{mlflow_port}'
