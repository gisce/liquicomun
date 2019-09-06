from setuptools import setup, find_packages

setup(
    name='liquicomun',
    version='0.1.1',
    packages=find_packages(),
    url='https://github.com/gisce/liquicomun',
    license='MIT',
    install_requires=['esios'],
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='Interact with REE liquicomun files',
)
