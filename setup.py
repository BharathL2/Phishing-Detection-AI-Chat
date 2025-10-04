from setuptools import setup, find_packages

setup(
    name='phish_chat_guard',
    version='1.0.0',
    description='Phish Chat Guard - Advanced Real-Time Phishing Detection for Chat Applications',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/phish-chat-guard',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=2.0.0',
        'flask-cors>=4.0.0',
        'pymongo>=4.0.0',
        'tldextract>=3.4.0',
        'python-dotenv>=0.19.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
        ]
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: Communications :: Chat',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)