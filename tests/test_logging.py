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
                                               {'acc': 0.9, 'F1': 0.7}, 'basic_component', 'NED', 'CPU', 'SVM', 17.4597)

        run = mlflow.get_run(run_id)

        artifact = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path='datasets/dataset.csv')

        with open(artifact) as f:
            artifact_data = f.read()

        self.assertEqual(dataset, artifact_data)

        self.assertEqual(2, len(run.data.metrics))
        self.assertEqual(8, len(run.data.params))
        self.assertEqual('test:latest', run.data.params['docker_image_tag'])
        self.assertEqual('CPU', run.data.params['hardware'])
        self.assertEqual(0.9, run.data.metrics['acc'])

    def test_test_logging(self):
        run_ids = self.logger.log_test_results([
            {
                'input': 'How much is the fish?',
                'true_target': 'Scooter',
                'predicted_target': 'Scouter',
                'docker_image_tag': 'MusicianAnnotator:latest',
                'runtime': 17.8901
            },
            {
                'input': 'Who made Thriller?',
                'true_target': 'Michael Jackson',
                'predicted_target': 'Michael Jackson',
                'docker_image_tag': 'MusicianAnnotator:latest',
                'runtime': 7.321
            }
        ])

        self.assertEqual(2, len(run_ids))

        run = mlflow.get_run(run_ids[0])

        self.assertEqual(5, len(run.data.params))
        self.assertEqual('Scooter', run.data.params['true_target'])

    def test_annotation_logging(self):
        run_id = self.logger.log_annotation('MusicianAnnotator:latest', 'How much is the fish?', 'Scooter', 'Scouter',
                                            'abc-def0123456789')

        run = mlflow.get_run(run_id)

        self.assertEqual(5, len(run.data.params))


if __name__ == '__main__':
    unittest.main()
