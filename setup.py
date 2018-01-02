from setuptools import setup, find_packages

setup(
    name='raptly',
    version='2.1.29',
    description='Remote Aptly client',
    long_description='Remote Aptly client',
    author='Art Crawford',
    author_email='pizzaiolo@a4pizza.com',
    url='https://github.com/a4pizza/test1',
    license='license',
    scripts=['src/main/bin/raptly'],
    packages=find_packages('src/main/python'),
    package_dir={'': 'src/main/python'}
)
