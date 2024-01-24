import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="printipy",
    version="1.2.0",
    author="Lawrence Weikum",
    description="Printify API for Python",
    url="https://github.com/lawrencemq/printipy",
    keywords=['printify', 'print on demand', 'api'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    py_modules=["printipy"],
    packages=setuptools.find_packages(exclude=['*tests*']),
    install_requires=[
        'requests',
        'dataclasses-json'
    ],
)
