from setuptools import setup, find_packages

setup(
    name='auth_sdk',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Django>=4.2',
        'djangorestframework>=3.12',
        'PyJWT>=2.1',
        'requests>=2.25',
    ],
)