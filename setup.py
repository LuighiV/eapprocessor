import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eapprocessor",
    version="0.0.1",
    author="Luighi Viton-Zorrilla",
    author_email="luighiavz@gmail.com",
    description="Scripts to process extracellular action potential recordings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LuighiV/eapprocessor",
    project_urls={
        "Bug Tracker": "https://github.com/LuighiV/eapprocessor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License ",
        "Operating System :: POSIX :: Linux ",
    ],
    packages=setuptools.find_packages(
        include=['eapprocessor',
                 'eapprocessor.*']
    ),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'colorlog',
        'numpy',
        'MEArec',
        # 'MEArec @ git+https://github.com/SpikeInterface/MEArec@6b560fe42dfef8c3910dcd70a76f71cadc18fc37',
        # 'MEArec @ git+https://github.com/SpikeInterface/MEArec@v1.7.2',
        'NEURON',
        'matplotlib',
        'h5py',
        'numpy',
        'efel',
        'MEArec',
        'PyYAML'
    ],
)
