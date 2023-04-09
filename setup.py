from setuptools import setup, find_packages

setup(
    name='sara_compis1_tools',
    version='0.0.4',
    description='A collection of tools for the Language Design course',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://github.com/MGonza20/Compis_Lab3',
    author='Sara Paguaga',
    author_email='sara.paguaga@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='Compiler',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'networkx',
        'graphviz'
    ]
)