from setuptools import find_packages, setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="apduboy",
    version="0.5.0",
    url="https://github.com/LedgerHQ/apduboy",
    author="Anirudha Bose",
    author_email="anirudha.bose@alumni.cern",
    description="APDUs for Humans",
    license="MIT",
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=[
        "construct<=2.10.61",
        "rlp>=2,<3",
        "ledgerwallet",
    ],
    extras_require={
        "dev": ["ipython", "black", "isort"],
        "test": ["pytest"],
    },
    keywords="ledger apdu nano ethereum bitcoin",
    packages=find_packages(include=["apduboy*"], exclude=["tests*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
