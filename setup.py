import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="monster-borg-remote-schrotty",
    version="0.0.1",
    author="Schrotty",
    author_email="rubenmaurer@live.de",
    description="A modified version of the 'pyController' package for usage with a ThunderBorg",
    long_description="A modified version of the 'pyController' package for usage with a ThunderBorg",
    long_description_content_type="text/markdown",
    url="https://github.com/Schrotty/MonsterBorgRemote",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)