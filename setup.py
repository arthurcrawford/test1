from setuptools import setup, find_packages


setup(
    name='sample',
    version='0.1.0',
    description='My description',
    long_description='long desc',
    author='Art Crawford',
    author_email='pizzaiolo@a4pizza.com',
    url='https://github.com/a4pizza/test1',
    license='license',
    packages=find_packages('src/main/python'),
    package_dir = { '': 'src/main/python' }
)
