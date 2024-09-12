from setuptools import setup, find_packages

setup(
    name="butterfly",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "openai",
        "python-dotenv",
        "requests",
        # Add other dependencies here
    ],
    entry_points={
        "console_scripts": [
            "butterfly=butterfly.butterfly:main",
        ],
    },
)