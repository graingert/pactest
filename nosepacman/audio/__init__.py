import pyglet.media
from pkg_resources import resource_filename


def loader(filename, streaming=False):
    return pyglet.media.load(
        filename=resource_filename(__name__, filename),
        streaming=streaming
    )


chomp = loader("pacman_chomp_converted.wav")
death = loader("pacman_death_converted.wav")


def play_chomp():
    return chomp.play()


def play_death():
    return death.play()

