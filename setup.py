from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pygge",
    version="0.0.1",
    author="Liam Huber",
    author_email="liam.huber@gmail.com",
    description="A package for what-you-type-is-what-you-get graphics editing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liamhuber/pygge",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)