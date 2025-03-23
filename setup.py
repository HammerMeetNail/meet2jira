from setuptools import setup, find_packages

setup(
    name="meet2jira",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "atlassian-python-api>=3.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "meet2jira=meet2jira.cli:main",
        ],
    },
)
