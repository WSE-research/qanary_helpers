import setuptools
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_requirements():
    reqs_path = os.path.join(__location__, 'requirements.txt')
    with open(reqs_path, encoding='utf8') as f:
        reqs = [line.strip() for line in f if not line.strip().startswith('#')]

    names = []
    for req in reqs:
        names.append(req)
    return {'install_requires': names}


setuptools.setup(
    name="qanary-helpers",
    version="0.2.0",
    author="Andreas Both, Aleksandr Perevalov",
    author_email="andreas.both@htwk-leipzig.de, aleksandr.perevalov@hs-anhalt.de",
    description="A package that helps to build components for the Qanary Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Perevalov/qanary_helpers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    **read_requirements()
)

