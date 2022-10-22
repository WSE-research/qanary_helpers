import unittest
from qanary_helpers.logging import MLFlowLogger
import mlflow
import os


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = MLFlowLogger(os.environ['MLFLOW_URI'], True, os.environ['MLFLOW_HOST'],
                                   os.environ['MLFLOW_PORT_ARTIFACT'])
        with open('dataset.csv', 'w') as f:
            f.write('test1,test2\n0,1\n2,3')

    def tearDown(self) -> None:
        os.remove('dataset.csv')

    def test_train_logging(self):
        with open('dataset.csv') as f:
            dataset = f.read()

        run_id = self.logger.log_train_results('test:latest', dataset, {'C': 0.5, 'balance': 'weighted'},
                                               {'param1': 3}, {'acc': 0.9, 'F1': 0.7}, 'basic_component', 'NED',
                                               'CPU', 'SVM', 17.4597)

        run = mlflow.get_run(run_id)

        artifact = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path='datasets/dataset.txt')

        with open(artifact) as f:
            artifact_data = f.read()

        self.assertEqual(dataset, artifact_data)

        metrics = mlflow.artifacts.load_dict(f'{run.info.artifact_uri}/model_metrics.json')
        self.assertEqual(2, len(metrics))

        config = mlflow.artifacts.load_dict(f'{run.info.artifact_uri}/config.json')
        self.assertEqual(1, len(config))

        self.assertEqual(8, len(run.data.params))
        self.assertEqual('test:latest', run.data.params['model_uuid'])
        self.assertEqual('CPU', run.data.params['hardware'])

    def test_test_logging(self):
        run_ids = self.logger.log_test_results([
            {
                'input': 'How much is the fish?',
                'true_target': {'value': 'Scooter'},
                'predicted_target': {'value': 'Scouter'},
                'model_uuid': 'MusicianAnnotator:latest',
                'runtime': 17.8901
            },
            {
                'input': 'Who made Thriller?',
                'true_target': {'value': 'Michael Jackson'},
                'predicted_target': {'value': 'Michael Jackson'},
                'model_uuid': 'MusicianAnnotator:latest',
                'runtime': 7.321
            }
        ])

        self.assertEqual(2, len(run_ids))

        run = mlflow.get_run(run_ids[0])

        artifact_uri = run.info.artifact_uri
        load_dict = mlflow.artifacts.load_dict(f'{artifact_uri}/true_target.json')

        self.assertEqual(3, len(run.data.params))
        self.assertEqual({'value': 'Scooter'}, load_dict)

    def test_annotation_logging(self):
        run_id = self.logger.log_annotation('MusicianAnnotator:latest', 'How much is the fish?', 'Scooter',
                                            'abc-def0123456789')

        run = mlflow.get_run(run_id)

        self.assertEqual(4, len(run.data.params))


if __name__ == '__main__':
    unittest.main()
