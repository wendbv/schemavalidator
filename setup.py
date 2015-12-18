from distutils.core import setup


setup(
    name='schemavalidator',
    packages=['schemavalidator'],
    version='0.1.0b1',
    description='A local JSON schema validator based on jsonschema',
    author='Daan Porru (Wend)',
    author_email='daan@wend.nl',
    license='MIT',
    url='https://github.com/wendbv/schemavalidator',
    keywords=['json schema', 'validator'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['jsonschema'],
    extras_require={
        'test': ['pytest', 'pytest-cov', 'coverage'],
    }
)
