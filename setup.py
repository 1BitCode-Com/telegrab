#!/usr/bin/env python3
"""
Setup script for Telegram Media Downloader
Updated 31/07/2025
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
    name="telegrab",
    version="2.0.0",
    author="1BitCode-Com",
    description="TeleGrab: The Ultimate Telegram Channel & Group Archiver. Designed to grab every photo, video, and document, bypassing API limits and handling expired links with ease.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/1BitCode-Com/telegrab",
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
            "telegrab=telegram_media_downloader:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="telegram, downloader, media, bot, api, grabber, archiver",
    project_urls={
        "Bug Reports": "https://github.com/1BitCode-Com/telegrab/issues",
        "Source": "https://github.com/1BitCode-Com/telegrab",
        "Documentation": "https://github.com/1BitCode-Com/telegrab#readme",
    },
) 
