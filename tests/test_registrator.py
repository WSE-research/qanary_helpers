from qanary_helpers.registrator import Registrator
from qanary_helpers.registration import Registration


def test_json_headers():
    json_headers = {
        "Content-type": "application/json",
        "Accept": "application/json"
    }

    name = "name"
    managementUrl = "managementUrl"
    healthUrl = "healthUrl"
    serviceUrl = "serviceUrl"
    source = "source"
    metadata = "metadata"

    registration = Registration(
        name=name,
        managementUrl=managementUrl,
        source=source,
        serviceUrl=serviceUrl,
        healthUrl=healthUrl,
        metadata=metadata
    )

    registrator_thread = Registrator(
        adminServerURL = "",
        adminServerUser = "",
        adminServerPassword = "",
        registration=registration
    )

    assert registrator_thread.jsonHeaders == json_headers
