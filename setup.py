from setuptools import setup, find_packages

setup(
    name='zulip2md',
    version='0.0.1',
    long_description="Convert Zulip export JSON to Markdown",
    author='rhiaro',
    author_email='amy@rhiaro.co.uk',
    url='https://rhiaro.co.uk',
    license='MIT',
    packages = find_packages(exclude=['docs', 'tests*']),
    entry_points={
        'console_scripts': [
            'zulip2md = zulip2md.zulip2md:cli',
        ],
    },
    install_requires=[
    ],
    test_suite='nose.collector',
    tests_require=['coverage', 'nose']
)
