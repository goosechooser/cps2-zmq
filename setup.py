from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='cps2_zmq',
    version='0.0.1',
    description='ya boi!!',
    long_description=readme,
    author='M B',
    author_email='dont@me',
    license=license,
    packages=find_packages())

