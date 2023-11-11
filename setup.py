from setuptools import setup, find_packages
from typing import List

HYPEN_E_DOT = '-e .'

def get_requirements(file_path:str) -> List[str]:
    requirements = []
    with open(file_path, 'r') as f:
        requirements = f.readlines()
        requirements = [req.replace('\n','') for req in requirements]
    requirements.remove(HYPEN_E_DOT)
    return requirements

setup(
    name='SmartNeev_Google_Maps_Review_Scrapper',
    version='0.0.1',
    author='Kush Joshi',
    author_email='kushjoshi16@gmail.com',
    install_requires=get_requirements('requirements.txt'),
    packages=find_packages()
)