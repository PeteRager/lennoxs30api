import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lennoxS30api",
    version="0.0.1",
    author="Pete Sage",
    author_email="pete.saged@icloud.com",
    description="API Wrapper for Lennox 30 Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thevoltagesource/myicomfort",
    packages=['lennoxs30api'],
    install_requires=[
        'aiohttp'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
