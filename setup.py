from setuptools import setup, find_packages

setup(
    name='spam_service',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'kafka-python',
        'joblib',
        'scikit-learn==1.0.2',
        'python-dotenv',
    ],
)