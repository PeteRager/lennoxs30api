import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lennoxs30api",
    version="0.0.8",
    description="API Wrapper for Lennox S30 Cloud API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PeteRager/lennoxs30api",
    author="Pete Sage",
    author_email="pete.saged@icloud.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["lennoxs30api"],
    install_requires=["aiohttp"],
)
