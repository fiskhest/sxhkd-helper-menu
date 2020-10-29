import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sxhkhm",
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version'],
    author="Johan Radivoj",
    author_email="johan+sxhkhm@radivoj.se",
    description="HotKey helper for sxhkd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fiskhest/sxhkd-helper-menu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'hkhelper.py = sxhkhm:main'
        ],
    },
    scripts=['sxhkhmenu'],
    python_requires='>=3.6',
)
