from setuptools import setup, find_packages

setup(
    name='playready_utils',
    version='0.1',
    description='Tools built to work with pyplayready',
    packages=find_packages(include=['playready_utils', 'playready_utils.*']),
    package_data={
    },
    entry_points={
        'console_scripts': ['playready-utils=playready_utils.main:cli'],
    },
    include_package_data=True,
    install_requires=[
        "cloup",
    ],
)
