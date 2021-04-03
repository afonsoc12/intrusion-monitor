import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="intrusion-monitor",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Afonso Costa",
    description="An SSH log watchdog, which exports failed login attempts to an InfluxDB timeseries database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/afonsoc12/intrusion-monitor",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests>=2.25.1,<3',
        'pygeohash>=1.2.0,<2',
        'influxdb>=5.3.1,<6'
    ],
    entry_points={
        'console_scripts': [
            'intrusion-monitor = intrusion_monitor.__main__:main'
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
