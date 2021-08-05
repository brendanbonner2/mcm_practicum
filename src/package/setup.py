import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lifecycle",
    version="0.0.1",
    author="Brendan Bonner",
    author_email="brendan.bonner2@mail.dcu.ie",
    description="Lifecycle management for Keras Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bonnerb2/lifecycle",
    project_urls={
        "Bug Tracker": "https://github.com/bonnerb2/lifecycle/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPG",
        "Operating System :: OS Independent",
    ],
    package_dir={"": ".."},
    packages=setuptools.find_packages(where=".."),
    python_requires=">=3.6",
        install_requires=[
        'DeepDiff',
        'pymongo',
    ],
)
