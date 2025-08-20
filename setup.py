from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='django-microservices-auth',
    version='1.0.0',
    author='agusabas',
    author_email='agus.abas@gmail.com',
    description='A Django REST Framework authentication SDK for microservices',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/agusabas/auth_sdk',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Django>=4.2,<6.0',
        'djangorestframework>=3.12,<4.0',
        'requests>=2.25,<3.0',
    ],
    extras_require={
        'redis': ['redis>=4.0,<6.0'],
        'dev': [
            'pytest>=7.0',
            'pytest-django>=4.5',
            'pytest-cov>=4.0',
            'black>=22.0',
            'flake8>=5.0',
            'mypy>=1.0',
        ],
    },
    keywords='django rest framework authentication jwt microservices',
    project_urls={
        'Bug Reports': 'https://github.com/agusabas/auth_sdk/issues',
        'Source': 'https://github.com/agusabas/auth_sdk',
    },
)
