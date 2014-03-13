from setuptools import setup, find_packages

setup(
    name='nose-pacman',
    version='0.1.0',
    description='A testrunner with a pacman progress bar',
    package_dir={'': 'src'},
    packages=find_packages(where="src", exclude=['ez_setup']),
    install_requires=['pyglet'],
    test_suite='nose.collector',
    url='https://github.com/graingert/pactest',
    include_package_data=True,
    entry_points={
        'nose.plugins.0.10': [
            "nosepacman = nose_pacman:PacmanPlugin"
        ]
    },
)
