from setuptools import setup

setup(
    name='litequeue',
    version='0.1.0',
    description='SQLite3-based lightweight work queue',
    long_description="Batteries-included queue, supports multithreading and multiprocessing",
    author='Maintained by Ian Ozsvald',
    author_email='ian@ianozsvald.com',
    url='https://github.com/ianozsvald/',
    license='MIT',
    packages=['litequeue', 'litequeue/tests', 'litequeue/config'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
