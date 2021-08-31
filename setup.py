from setuptools import setup

version = '1.0.0'

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name="pygvm",
    version=version,
    description='pygvm',
    long_description=open('README.md').read(),
    author='JiaWei Cheng',
    author_email='cjwpython@163.com',
    packages=["pygvm"],
    zip_safe=False,
    install_requires=requires,
)
