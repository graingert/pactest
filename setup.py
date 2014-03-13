from setuptools import setup, find_packages

setup(
    name='nose-pacman',
    version='0.1.0',
    description='A testrunner with a pacman progress bar',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=['pyglet'],
    test_suite='nose.collector',
    url='https://github.com/neob91/nose-pacman',
    include_package_data=True,
    entry_points={
        'nose.plugins.0.10': [
            "nosepacman = nosepacman:PacmanPlugin"
        ]
    },
)
