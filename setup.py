import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qanary-helpers",
    version="0.0.10",
    author="Andreas Both, Aleksandr Perevalov",
    author_email="andreas.both@hs-anhalt.de, aleksandr.perevalov@hs-anhalt.de",
    description="A package that helps to build components for the Qanary framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Perevalov/qanary_helpers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

