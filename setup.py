from setuptools import setup, find_packages

setup(
    name='saftools',
    version='1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        '': ['accelergy/data/*.csv'],
    },
    entry_points={
        'console_scripts': [
            'safinfer = safinfer:main',
            'safmodel = safmodel:main',
            'safsearch = safsearch:main'
        ]
    },
)
