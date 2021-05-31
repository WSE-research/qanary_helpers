from qanary_helpers.registrator import Registrator
from qanary_helpers.registration import Registration

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
    admin_server_url="",
    admin_server_user="",
    admin_server_password="",
    registration=registration
)


def test_json_headers():
    json_headers = {
        "Content-type": "application/json",
        "Accept": "application/json"
    }

    assert registrator_thread.json_headers == json_headers


def test_admin_server_url():
    assert 'instances' in registrator_thread.admin_server_url


def test_is_stopped():
    assert registrator_thread.is_stopped() == False
