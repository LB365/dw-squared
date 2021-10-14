from setuptools import setup

REQUIREMENTS = [
	'datawrapper',
	'pandas',
    'psyl',
    'tshistory',
    'tqdm',
]

setup(
    name='dw-squared',
    version='1.0',
    packages=['dw_squared'],
    package_dir={
        'dw_squared': 'dw_squared',
    },
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'dw=dw_squared.cli:view',
        ],
    },
)
