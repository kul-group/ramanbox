from setuptools import setup


setup(
    name='ramanbox',
    version='0.1.0',
    description='A Python package for organizing SERS spectra',
    url='https://github.com/kul-group/ramanbox',
    author='Dexter Antonio',
    author_email='dexter.d.antonio@gmail.com',
    license='MIT',
    packages=['ramanbox'],
    install_requires=['xarray','numpy','pandas', 'netCDF4', 'gitpython'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.8',
    ],
)
