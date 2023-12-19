from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='power-tracker',
    version='1.0',
    author='Daniel Davis',
    description="A Raspberry Pi based system for displaying New Zealand's national power grid data",
    long_description=long_description,
    url='https://github.com/DanielDavisEE/PowerTracker',
    python_requires='>=3.9, <4',
    package_dir={'': 'src'},
    packages=['power_tracker'],
    install_requires=[
        'lxml',
        'requests',
        'selenium',
        'pandas',
        'beautifulsoup4',
        'matplotlib'
    ],
    package_data={
    },
    entry_points={
    }
)
