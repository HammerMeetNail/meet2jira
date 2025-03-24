from setuptools import setup, find_packages

setup(
    name='meet2jira',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'ollama',
        'python-dotenv',
        'requests',
        'argparse',
        'atlassian-python-api'
    ],
    entry_points={
        'console_scripts': [
            'meet2jira=meet2jira.cli:main',
        ],
    },
    python_requires='>=3.8',
)
