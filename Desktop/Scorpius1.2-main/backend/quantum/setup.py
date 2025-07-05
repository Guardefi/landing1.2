"""
Setup script for Scorpius Enterprise Quantum Security Platform
"""

import os

from setuptools import find_packages, setup


# Read long description from README
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Scorpius Enterprise Quantum Security Platform"


# Read version
def read_version():
    version_file = os.path.join("scorpius", "__init__.py")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "2.0.0"


setup(
    name="scorpius-enterprise",
    version=read_version(),
    author="Scorpius Development Team",
    author_email="dev@scorpius-quantum.com",
    description="Enterprise-grade quantum-resistant cryptography and blockchain security platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/scorpius-quantum/enterprise",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.9",
    install_requires=[
        "asyncio-mqtt>=0.13.0",
        "cryptography>=41.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.4.0",
        "python-dateutil>=2.8.0",
        "PyYAML>=6.0.0",
        "redis>=4.6.0",
        "requests>=2.31.0",
        "click>=8.1.0",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
    ],
    extras_require={
        "enterprise": [
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0",
            "psycopg2-binary>=2.9.0",
            "prometheus-client>=0.17.0",
            "structlog>=23.1.0",
            "elasticsearch>=8.9.0",
            "celery>=5.3.0",
        ],
        "quantum": [
            "pqcrypto>=0.10.0",
            "scipy>=1.11.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "scorpius=scorpius.cli.main:cli",
        ],
    },
    package_data={
        "scorpius": [
            "config/*.yml",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "quantum-cryptography",
        "post-quantum",
        "blockchain-security",
        "enterprise-security",
        "cryptography",
        "quantum-resistant",
        "lattice-based-crypto",
        "enterprise-platform",
    ],
)
