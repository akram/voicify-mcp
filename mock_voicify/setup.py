from setuptools import setup, find_packages

setup(
    name="voicify",
    version="1.0.0",
    packages=find_packages(),
    description="Mock Voicify TTS package for development",
    long_description="This is a mock implementation of Voicify TTS for development and testing purposes.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
)
