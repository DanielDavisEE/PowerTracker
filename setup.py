from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='power-tracker',
    version='1.0',
    author='Daniel Davis',
    description='',
    long_description=long_description,
    url='https://github.com/DanielDavisEE/PowerTracker',
    python_requires='>=3.10, <4',
    package_dir={'': 'src'},
    packages=['power_tracker'],
    install_requires=[
        'requests',
        'selenium',
        'beatifulsoup4',
        'matplotlib'
    ],
    package_data={
    },
    entry_points={
    }
)
