from setuptools import setup, find_packages

setup(
    name='saftools',
    version='1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        '': ['accelergy/data/*.csv',
             'saflib/microarchitecture/modelscript/*.yaml', 
             'saflib/microarchitecture/taxoscript/*.yaml', 
             'saflib/rulesets/taxo/*.yaml', 
             'saflib/rulesets/taxo/base_ruleset/*.yaml', 
             'saflib/rulesets/taxo/microarchitecture_from_saf/*.yaml'
             ],
    },
    entry_points={
        'console_scripts': [
            'safinfer = safinfer:main',
            'safmodel = safmodel:main',
            'safsearch = safsearch:main'
        ]
    },
)

'''
, 
             'saflib/microarchitecture/modelscript/*.yaml', 
             'saflib/microarchitecture/taxoscript/*.yaml', 
             'saflib/rulesets/taxo/*.yaml', 
             'saflib/rulesets/taxo/base_ruleset/*.yaml', 
             'saflib/rulesets/taxo/microarchitecture_from_saf/*.yaml'
'''