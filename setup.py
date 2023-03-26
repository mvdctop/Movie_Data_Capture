from setuptools import setup, find_packages
from Movie_Data_Capture import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as f:
    requirements = f.read().strip().splitlines()


setup(
    name='Movie_Data_Capture',
    version=VERSION,
    description='A tool to capture jav movie data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author='MDC',
    url="https://github.com/yoshiko2/Movie_Data_Capture",
    license='GPL-3.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'mdc = Movie_Data_Capture.Movie_data_Capture:main'
        ]
    },
)
