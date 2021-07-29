from setuptools import find_packages, setup

setup(
    name="ledger-apduboy",
    version="0.1.0",
    url="https://github.com/LedgerHQ/apduboy",
    author="Anirudha Bose",
    author_email="anirudha.bose@alumni.cern",
    description="APDUs for Humans",
    long_description="",
    long_description_content_type="text/markdown",
    install_requires=[
        "construct>=2.10.0",
    ],
    extras_require={
        "ethereum": ["rlp>=2,<3"],
        "dev": ["ipython", "black", "isort"],
        "test": ["pytest"],
    },
    keywords="ledger apdu nano ethereum bitcoin",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
