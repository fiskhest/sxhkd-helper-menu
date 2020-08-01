import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rhkhm",
    version="0.1.1",
    author="Johan Radivoj",
    author_email="johan+rhkhm@radivoj.se",
    description="HotKey helper for sxhkd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fiskhest/rhkhm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'hkhelper.py = rhkhm:main'
        ],
    },
    scripts=['rhkhmenu'],
    python_requires='>=3.6',
)
