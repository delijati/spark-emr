from setuptools import setup


setup(
    name='spark_emr_dummy',
    version="0.0.1",
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'spark_emr_dummy.py = main:main'
        ],
    }
)
