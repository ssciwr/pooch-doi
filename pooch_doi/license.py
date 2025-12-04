class License:
    ...


class SPDXLicense(License):
    spdx_id: str


class CustomLicense(License):
    title: str
    description: str
    link: str
