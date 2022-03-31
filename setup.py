import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()
TESTS_REQUIRE = (HERE / "requirements-dev.txt").read_text().splitlines()[1:]

setup(
    name="web-bricks",
    version="0.0.3",
    description="Page Object constructor for UI automation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yuriy Sagitov",
    author_email="yu.sagitov@2gis.ru",
    python_requires=">=3.8.0",
    url="https://github.com/2gis-test-labs/web-bricks",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
)
