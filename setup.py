"""setup.py

Packaging for direct pypi distribution and cli entrypoints

"""
from setuptools import setup, find_packages
from os import path
from codecs import open

__library_name__ = "southwest"
__here__ = path.dirname(__file__)

with open(path.join(__here__, "README.md"), "r", "utf-8") as f:
    __readme__ = f.read()

with open(path.join(__here__, __library_name__, "VERSION"), "r") as f:
    __version__ = f.read().strip()


setup(
    name="SouthwestCheckin",
    description="Python script to checkin to a Southwest Flight",
    long_description=__readme__,
    long_description_content_type="text/markdown",
    url="https://github.com/pyro2927/SouthwestCheckin",
    license="GPL-3.0",
    packages=find_packages(exclude=["tests"]),
    version=__version__,
    install_requires=[
        "datetime",
        "docopts",
        "python-dateutil",
        "pytz",
        "requests",
        "uuid",
        "vcrpy",
    ],
    extras_require={
        "dev": ["pycodestyle", "pytest", "pytest-cov", "pytest-mock", "requests_mock",]
    },
    entry_points={
        "console_scripts": ["checkin={}.checkin:checkin".format(__library_name__)]
    },
    package_data={"": ["README.md", "LICENSE"], __library_name__: ["VERSION"]},
    include_package_data=True,
)
