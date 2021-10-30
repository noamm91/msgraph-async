import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="msgraph-async",
    version="0.1.7",
    author="Noam Meerovitch",
    author_email="noamm91@gmail.com",
    description="Client for using Microsoft Graph API asynchronously",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://noamm91.github.io/msgraph-async",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
