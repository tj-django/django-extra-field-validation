from io import open

from setuptools import find_packages, setup

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = ['Django>=2.1<3.0']

version = __import__('django_dynamic_model_validation').__version__

setup(
    name='django-dynamic-model-validation',
    version=version,
    description='',
    long_description=readme,
    author='Tonye Jack',
    author_email='jtonye@ymail.com',
    maintainer='Tonye Jack',
    maintainer_email='jtonye@ymail.com',
    url='https://github.com/jackton1/django-dynamic-model-validation.git',
    license='MIT/Apache-2.0',
    keywords=['django', 'model validation', 'django models'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],
    extras_require={'development': ['pip-tools==3.1.0']},
    packages=find_packages(exclude=['test*']),
)
