import os
import io

from setuptools import find_packages, setup

install_requires = ['future==0.17.1']

test_requires = [
    'tox==3.1.2',
    'pytest-django==3.4.4',
    'pluggy>=0.7',
    'mock==2.0.0',
    'codacy-coverage==1.3.10',
]

deploy_requires = [
    'readme_renderer[md]',
    'bumpversion==0.5.3',
]

lint_requires = [
    'flake8==3.4.1',
    'yamllint==1.10.0',
    'isort==4.2.15',
]

local_dev_requires = [
    'Django>=1.11.18',
    'pip-tools==3.1.0',
    'check-manifest==0.37',
]

extras_require = {
    'development': [
        local_dev_requires,
        install_requires,
        test_requires,
        lint_requires,
    ],
    'test': test_requires,
    'lint': lint_requires,
    'deploy': deploy_requires,
    'tox': local_dev_requires,
}

BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, 'README.rst')

if os.path.isfile(README_PATH):
    with io.open(README_PATH, encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = ''

VERSION = (0, 1, 11)

version = '.'.join(map(str, VERSION))

setup(
    name='django-dynamic-model-validation',
    version=version,
    description='Extra django model validation.',
    python_requires='>=2.6',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='Tonye Jack',
    author_email='jtonye@ymail.com',
    maintainer='Tonye Jack',
    maintainer_email='jtonye@ymail.com',
    url='https://github.com/jackton1/django-dynamic-model-validation.git',
    license='MIT/Apache-2.0',
    keywords=[
        'django', 'model validation', 'django models', 'django object validation',
        'field validation', 'conditional validation', 'cross field validation',
        'django validation', 'django validators', 'django custom validation',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
    ],
    install_requires=install_requires,
    tests_require=['coverage', 'pytest'],
    extras_require=extras_require,
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests*', 'demo', 'manage.*']),
)
