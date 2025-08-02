#!/usr/bin/env python3
"""
Setup script for Telegram Media Downloader
Updated 02/08/2025
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="telegram-media-downloader",
    version="2.0.0",
    author="1BitCode-Com",
    description="The most advanced and stable Telegram media downloader. Features robust parallel downloading, intelligent error handling (FloodWait, Expired Links), and a configurable chunk-based mechanism to bypass API limits. Optimized for massive archives.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/1BitCode-Com/telegram-media-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "telegram-downloader=telegram_media_downloader:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="telegram, downloader, media, bot, api",
    project_urls={
        "Bug Reports": "https://github.com/1BitCode-Com/telegram-media-downloader/issues",
        "Source": "https://github.com/1BitCode-Com/telegram-media-downloader",
        "Documentation": "https://github.com/1BitCode-Com/telegram-media-downloader#readme",
    },
) 
