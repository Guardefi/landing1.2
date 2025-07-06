import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="honeypot-detector",
    version="1.0.0",
    author="Enterprise Security Team",
    author_email="security@example.com",
    description="Enterprise-grade smart contract honeypot detector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youraccount/honeypot-detector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.0",
        "pydantic>=1.10.0",
        "motor>=3.1.1",
        "web3>=6.1.0",
        "redis>=4.5.1",
        "aiohttp>=3.8.4",
        "prometheus-client>=0.16.0",
        "celery>=5.2.7",
        "scikit-learn>=1.2.2",
        "joblib>=1.2.0",
        "numpy>=1.24.2",
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "honeypot-api=api.main:start",
            "honeypot-worker=worker.celery_app:start",
        ],
    },
)
