import os
import codecs
from setuptools import setup, find_packages

README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'),
                     'r', encoding='utf-8').read()

setup(
    name="graph_validations",
    version='0.2',
    description='Validations And Transformations For Schematic Editor Simple Graphs',
    packages=find_packages(),
    long_description=README,
    long_description_content_type='text/markdown',
    keywords="schematic editor validations",
    install_requires=['Click', "Typhoon-HIL-API"],
    license='MIT',
    author='Balsa Bulatovic',
    author_email='baki.b.2k02@gmail.com',

    entry_points={
        'console_scripts': [
            'graph_validations = myvalidator.cli:cli'
        ],

        'validation_commands': [
            'validate = myvalidator.cli:validate1',
            'list_validations = myvalidator.validations:validation_list'
        ]
    }
)
