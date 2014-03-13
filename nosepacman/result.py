from __future__ import with_statement

from blessings import Terminal
from nose.plugins.skip import SkipTest
from nose.result import TextTestResult
from nose.util import isclass

from nosepacman.pacman import PacmanDisplay, NullDisplay
from nosepacman.tracebacks import format_traceback, extract_relevant_tb
from nosepacman.utils import nose_selector, index_of_test_frame


class PacmanResult(TextTestResult):
    """Test result which updates a progress bar instead of printing dots

    Nose's ResultProxy will wrap it, and other plugins can still print
    stuff---but without smashing into my progress bar, care of my Plugin's
    stderr/out wrapping.

    """

    def __init__(self, cwd, total_tests, stream, config=None):
        super(PacmanResult, self).__init__(stream, None, 0, config=config)
        self._cwd = cwd
        self._options = config.options
        self._term = Terminal(stream=stream,
                              force_styling=config.options.with_styling)

        if self._term.is_a_tty or self._options.with_bar:
            # 1 in case test counting failed and returned 0
            self.display = PacmanDisplay(self._term)
        else:
            self.display = NullDisplay()

        # Declare errorclass-savviness so ErrorClassPlugins don't monkeypatch
        # half my methods away:
        self.errorClasses = {}

    def startTest(self, test):
        """Update the progress bar."""
        super(PacmanResult, self).startTest(test)

    def _printTraceback(self, test, err):
        """Print a nicely formatted traceback.

        :arg err: exc_info()-style traceback triple
        :arg test: the test that precipitated this call

        """
        # Don't bind third item to a local var; that can create
        # circular refs which are expensive to collect. See the
        # sys.exc_info() docs.
        exception_type, exception_value = err[:2]
        # TODO: In Python 3, the traceback is attached to the exception
        # instance through the __traceback__ attribute. If the instance
        # is saved in a local variable that persists outside the except
        # block, the traceback will create a reference cycle with the
        # current frame and its dictionary of local variables. This will
        # delay reclaiming dead resources until the next cyclic garbage
        # collection pass.

        extracted_tb = extract_relevant_tb(
            err[2],
            exception_type,
            exception_type is test.failureException)
        test_frame_index = index_of_test_frame(
            extracted_tb,
            exception_type,
            exception_value,
            test)
        if test_frame_index:
            # We have a good guess at which frame is the test, so
            # trim everything until that. We don't care to see test
            # framework frames.
            extracted_tb = extracted_tb[test_frame_index:]

    def _recordAndPrintHeadline(self, test, error_class, artifact):
        """Record that an error-like thing occurred, and print a summary.

        Store ``artifact`` with the record.

        Return whether the test result is any sort of failure.

        """
        # We duplicate the errorclass handling from super rather than calling
        # it and monkeying around with showAll flags to keep it from printing
        # anything.
        is_error_class = False
        for cls, (storage, label, is_failure) in self.errorClasses.items():
            if isclass(error_class) and issubclass(error_class, cls):
                if is_failure:
                    test.passed = False
                storage.append((test, artifact))
                is_error_class = True
        if not is_error_class:
            self.errors.append((test, artifact))
            test.passed = False

        is_any_failure = not is_error_class or is_failure
        #self._printHeadline(label if is_error_class else 'ERROR',
        #                    test,
        #                    is_failure=is_any_failure)
        return is_any_failure

    def addSkip(self, test, reason):
        """Catch skipped tests in Python 2.7 and above.

        Though ``addSkip()`` is deprecated in the nose plugin API, it is very
        much not deprecated as a Python 2.7 ``TestResult`` method. In Python
        2.7, this will get called instead of ``addError()`` for skips.

        :arg reason: Text describing why the test was skipped

        """
        self._recordAndPrintHeadline(test, SkipTest, reason)
        # Python 2.7 users get a little bonus: the reason the test was skipped.
        if isinstance(reason, Exception):
            reason = reason.message
        #if reason and self._options.show_advisories:
        #    with self.bar.dodging():
        #        self.stream.writeln(reason)

    def addError(self, test, err):
        super(PacmanResult, self).addError(test, err)
        # We don't read this, but some other plugin might conceivably expect it
        # to be there:
        excInfo = self._exc_info_to_string(err, test)
        is_failure = self._recordAndPrintHeadline(test, err[0], excInfo)
        #if is_failure:
        #    self._printTraceback(test, err)
        self.display.test_error()

    def addFailure(self, test, err):
        super(PacmanResult, self).addFailure(test, err)
        #self._printHeadline('FAIL', test)
        #self._printTraceback(test, err)
        self.display.test_failed()

    def addSuccess(self, test):
        super(PacmanResult, self).addSuccess(test)
        self.display.test_passed()

    def printSummary(self, start, stop):
        """As a final summary, print number of tests, broken down by result."""
        self.display.eat()
        self.printErrors()
        def renderResultType(type, number, is_failure):
            """Return a rendering like '2 failures'.

            :arg type: A singular label, like "failure"
            :arg number: The number of tests with a result of that type
            :arg is_failure: Whether that type counts as a failure

            """
            # I'd rather hope for the best with plurals than totally punt on
            # being Englishlike:
            ret = '%s %s%s' % (number, type, 's' if number != 1 else '')
            if is_failure and number:
                ret = self._term.bold(ret)
            return ret

        # Summarize the special cases:
        counts = [('test', self.testsRun, False),
                  ('failure', len(self.failures), True),
                  ('error', len(self.errors), True)]
        # Support custom errorclasses as well as normal failures and errors.
        # Lowercase any all-caps labels, but leave the rest alone in case there
        # are hard-to-read camelCaseWordBreaks.
        counts.extend([(label.lower() if label.isupper() else label,
                        len(storage),
                        is_failure)
                        for (storage, label, is_failure) in
                            self.errorClasses.values() if len(storage)])
        summary = (', '.join(renderResultType(*a) for a in counts) +
                   ' in %.1fs' % (stop - start))

        # Erase progress bar. Bash doesn't clear the whole line when printing
        # the prompt, leaving a piece of the bar. Also, the prompt may not be
        # at the bottom of the terminal.

        if self.wasSuccessful():
            self.stream.write(self._term.bold_green('OK!  '))
        self.stream.writeln(summary)
