from setuptools import setup, find_packages

setup(
    name="semenhance",
    version="0.1.0",
    description="SemEnhance fine-tuning CLI wrapper",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    py_modules=["semenhance_finetune"],
    entry_points={
        'console_scripts': [
            'semenhance.finetune=semenhance_finetune:main',
        ],
    },
    python_requires='>=3.6',
    install_requires=[
        # Add any dependencies here
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
