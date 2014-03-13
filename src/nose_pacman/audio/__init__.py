import pyglet.media
from pkg_resources import resource_filename


def loader(filename, streaming=False):
    return pyglet.media.load(
        filename=resource_filename(__name__, filename),
        streaming=streaming
    )


class PacmanAudio(object):

    def __init__(self):
        self.player = pyglet.media.Player()
        self.sources = {
            "intro": loader("pacman_beginning_converted.wav"),
            "moving": loader("pacman_chomp_converted.wav", streaming=False),
            "die": loader("pacman_death_converted.wav")
        }

    def play(self):
        self.player.play()
