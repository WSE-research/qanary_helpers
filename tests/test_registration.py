from qanary_helpers.registration import Registration


def test_registration():
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

    assert registration.name == name
    assert registration.managementUrl == managementUrl
    assert registration.healthUrl == healthUrl
    assert registration.serviceUrl == serviceUrl
    assert registration.source == source
    assert registration.metadata == metadata
