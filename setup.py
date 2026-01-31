from setuptools import setup, find_packages

setup(
    name="solar_tracking",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sunpy[all]", "opencv-python", "numpy", "matplotlib", "astropy"
    ],
    entry_points={
        "console_scripts": [
            "solar-tracking=solar_tracking.cli:main",
        ]
    },
)
