from qanary_helpers.configuration import Configuration
import os 


def test_configuration():
    configuration = Configuration(os.path.join("configs", "app.conf"),
        [
            'springbootadminserverurl',
            'springbootadminserveruser',
            'springbootadminserverpassword',
            'servicehost',
            'serviceport',
            'servicename',
            'servicedescription',
            'serviceversion'
        ])

    assert len(configuration.demandedConfigurationKeys) == 0
