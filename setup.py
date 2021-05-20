from setuptools import setup, find_packages

setup(
    name='liquicomun',
    version='0.4.0',
    packages=find_packages(),
    url='https://github.com/gisce/liquicomun',
    license='MIT',
    install_requires=[
        'esios',
        'pytz',
        'future',
    ],
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='Interact with REE liquicomun files',
)
