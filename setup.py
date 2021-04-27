from setuptools import setup, find_packages

setup(
    name="riden",
    version="0.1.1",
    description="A python library for Riden RD6006-RD6018 power supplies",
    url="https://github.com/ShayBox/Riden.git",
    license="MIT",
    author="Shayne Hartford",
    packages=find_packages(),
    install_requires=["modbus_tk", "pyserial"]
)
