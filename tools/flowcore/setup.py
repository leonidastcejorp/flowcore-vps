"""FlowCore - Enterprise Workflow Automation Toolkit"""
from setuptools import setup, find_packages

setup(
    name="flowcore",
    version="1.0.0",
    description="Enterprise workflow automation toolkit for web operations",
    author="Leonidas",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "aiohttp>=3.9.0",
        "aiohttp-socks>=0.8.0",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.11",
)
