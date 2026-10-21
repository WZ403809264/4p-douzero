import setuptools

VERSION = '1.0.0'

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="4p-douzero",
    version=VERSION,
    author="WZ403809264",
    author_email="403809264@qq.com",
    description="4-player DouDizhu AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/WZ403809264/4p-douzero",
    license='Apache License 2.0',
    keywords=["DouDizhu", "4-player", "4-player DouDizhu", "AI", "Torch", "Poker"],
    packages=setuptools.find_packages(),
    install_requires=[
        'torch'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
)
