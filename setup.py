from setuptools import setup, find_packages

setup(
    name="set_aws_mfa",
    packages=find_packages("src"),
    package_dir={'': 'src'}
)
