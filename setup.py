from setuptools import setup, find_packages
from playready_utils import __version__

setup(
    name='playready_utils',
    version=__version__,
    author="8c",
    description='Tools built to work with playready and pyplayready',
    packages=find_packages(include=['playready_utils', 'playready_utils.*']),
    package_data={
    },
    entry_points={
        'console_scripts': ['playready-utils=playready_utils.main:cli'],
    },
    include_package_data=True,
    install_requires=[
        "cloup",
        'construct==2.8.8',
        'coloredlogs',
    ],
)