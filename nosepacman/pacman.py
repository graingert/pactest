from __future__ import with_statement
from itertools import cycle
from signal import signal, SIGWINCH
import time

__all__ = ['ProgressBar', 'NullProgressBar']


DOT_SIGN = u'.'
FAIL_SIGN = u'F'
ERROR_SIGN = u'E'
SKIP_SIGN = u'S'
PACMAN_SIGN = u'C'
CRASH_SIGN = u'X'


class PacmanDisplay(object):
    _locked = False
    _tests_showed = 0
    _queue = []

    def __init__(self, term):
        self._term = term

        self._measure_terminal()
        signal(SIGWINCH, self._measure_terminal)

    def _measure_terminal(self):
        self.lines, self.cols = (self._term.height, self._term.width)

    def test_passed(self):
        self._add_dot(DOT_SIGN)

    def test_failed(self):
        self._add_dot(FAIL_SIGN)

    def test_error(self):
        self._add_dot(ERROR_SIGN)

    def test_skipped(self):
        self._add_dot(SKIP_SIGN)

    def _add_dot(self, char):
        self._queue.append(char)
        if self._locked:
            return

        self._redraw()

    def _redraw(self):
        self._locked = True
        self._flush()
        self._flush(''.join(self._queue))
        self._locked = False

    def _flush(self, content=None):
        with self._term.location():
            self._term.stream.write(content or self._term.clear_eos)
        self._term.stream.flush()

    def eat(self):
        for i, char in enumerate(self._queue):
            if char in [DOT_SIGN, SKIP_SIGN]:
                new_char = ' '
            elif char in [FAIL_SIGN, ERROR_SIGN]:
                new_char = CRASH_SIGN
            self._queue[i] = PACMAN_SIGN
            self._redraw()
            self._queue[i] = new_char
            time.sleep(0.1)
        self._flush()


class Null(object):
    def __getattr__(self, *args, **kwargs):
        """Return a boring callable for any attribute accessed."""
        return lambda *args, **kwargs: None

    # Beginning in Python 2.7, __enter__ and __exit__ aren't looked up through
    # __getattr__ or __getattribute__:
    # http://docs.python.org/reference/datamodel#specialnames
    __enter__ = __exit__ = __getattr__


class NullDisplay(Null):
    """``ProgressBar`` workalike that does nothing

    Comes in handy when you want to have an option to hide the progress bar.

    """
    def dodging(self):
        return Null()  # So Python can call __enter__ and __exit__ on it
