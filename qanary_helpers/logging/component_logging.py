import os
import mlflow
from .config import mlflow_uri, test_params, sftp, mlflow_host, mlflow_port_artifact, test_dicts
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union
from uuid import uuid4
from shutil import rmtree
from .get_ssh_key import load_ssh_host_key
import logging

logging.getLogger("paramiko").setLevel(logging.WARNING)


class QanaryComponentLogger(ABC):
    """
    Class providing a Logging interface for Qanary components
    """
    @abstractmethod
    def log_train_results(self, model_uuid: str, train_data: str, test_data: str, hyperparameters: Dict[str, Any],
                          config: Dict[str, Any], metrics: Dict[str, Any], component_name: str, component_type: str,
                          hardware: str, model: str, time: float) -> Any:
        """
        Logging train results of the Qanary component

        :param model_uuid: UUID of the trained model
        :param train_data: train dataset of the Qanary component
        :param test_data: test dataset of the Qanary component
        :param hyperparameters: dictionary of [hyperparameter_name, value] pairs
        :param config: model config as dictionary
        :param metrics: dictionary of [metric_name, value] pairs
        :param component_name: name of the Qanary component
        :param component_type: type of the Qanary component
        :param hardware: used hardware for training
        :param model: name of the used model
        :param time: runtime of the training
        :return: Identifier for the logged train results
        """

    @abstractmethod
    def log_test_results(self, questions: List[Dict[str, Union[str, float]]]) -> Any:
        """
        Logging test results for all test questions. Each question dictionary requires the keys
        "input", "true_target", "predicted_target", "model_uuid" and "runtime"

        :param questions: list of parameters that have to be logged for each question
        :return: Identifier for the logged test results
        """

    @abstractmethod
    def log_annotation(self, model_uuid: str, question: str, predicted_target: str, qanary_graph_id: str) -> Any:
        """
        Logging the data of the created annotation of a Qanary component

        :param model_uuid: UUID of the used model
        :param question: question as string data
        :param predicted_target: target predicted by the component
        :param qanary_graph_id: Qanary Graph ID of the annotation
        :return: Identifier for the logged annotation data
        """


class MLFlowLogger(QanaryComponentLogger):
    """
    Class providing a Logging service for Qanary components with MLFlow
    """
    def __init__(self, uri=mlflow_uri, use_sftp=sftp, ssh_host=mlflow_host, ssh_port=mlflow_port_artifact):
        """
        Initializes a Logger for Qanary components with MLFlow. Default setup connects to http://localhost:5000 with
        local artifact storage.

        :param uri: MLFlow tracking URI
        :param use_sftp: True, if MLFlow uses SFTP artifact storage, else False
        :param ssh_host: SFTP hostname
        :param ssh_port: SSH port of SFTP storage host
        """
        mlflow.set_tracking_uri(uri)

        if use_sftp:
            load_ssh_host_key(ssh_host, ssh_port)

    def log_train_results(self, model_uuid: str, train_data: str, test_data: str, hyperparameters: Dict[str, Any],
                          config: Dict[str, Any], metrics: Dict[str, float], component_name: str, component_type: str,
                          hardware: str, model: str, time: float) -> Any:
        mlflow.set_experiment('AutoML Model Training')

        temp_path = str(uuid4())
        os.mkdir(temp_path)

        datasets = []

        for dataset, suffix in zip([train_data, test_data], ['train', 'test']):
            temp_dataset = f'{temp_path}/dataset_{suffix}.txt'

            # store dataset to filesystem
            with open(temp_dataset, 'w') as f:
                f.write(dataset)

                datasets.append(temp_dataset)

        with mlflow.start_run() as run:
            # Log train parameters and model results
            try:
                mlflow.log_param('model_uuid', model_uuid)

                for dataset in datasets:
                    mlflow.log_artifact(dataset, 'datasets')

                for parameter in hyperparameters:
                    mlflow.log_param(parameter, hyperparameters[parameter])

                mlflow.log_dict(metrics, 'model_metrics.json')
                mlflow.log_dict(config, 'config.json')
                mlflow.log_param('component_name', component_name)
                mlflow.log_param('component_type', component_type)
                mlflow.log_param('hardware', hardware)
                mlflow.log_param('model', model)
                mlflow.log_param('time', time)
            # delete temp dataset file
            finally:
                rmtree(temp_path)

            return run.info.run_id

    def log_test_results(self, questions: List[Dict[str, Any]]) -> Any:
        mlflow.set_experiment('AutoML Model Testing')

        run_ids = []

        for question in questions:
            with mlflow.start_run() as run:
                # log all provided data as parameters
                for test_param in test_params:
                    mlflow.log_param(test_param, question[test_param])

                for test_dict in test_dicts:
                    mlflow.log_dict(question[test_dict], f'{test_dict}.json')

                run_ids.append(run.info.run_id)

        return run_ids

    def log_annotation(self, model_uuid: str, question: str, predicted_target: str, qanary_graph_id: str) -> Any:
        mlflow.set_experiment('AutoML Component Annotations')

        with mlflow.start_run() as run:
            mlflow.log_param('model_uuid', model_uuid)
            mlflow.log_param('input', question)
            mlflow.log_param('predicted_target', predicted_target)
            mlflow.log_param('qanary_graph_id', qanary_graph_id)

            return run.info.run_id
