from qanary_helpers.configuration import Configuration
import os 


def test_configuration():
    configuration = Configuration(os.path.join(os.getcwd(), "tests", "configs", "app.conf"),  # works if executed with pytest
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
