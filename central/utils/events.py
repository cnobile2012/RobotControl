#
# central/utils/event.py
#

"""
by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import select, subprocess


class Event(object):
    INPUT = select.EPOLLIN
    OUTPUT = select.EPOLLOUT
    ERROR = select.EPOLLERR
    HANGUP = select.EPOLLHUP
    PRI_INPUT = select.EPOLLPRI
    LEVEL = 0
    EDGE = 1

    def __init__(self, sizehint=-1):
        self._sizehint = sizehint
        self.__epoll = None
        self._queue = {}
        self._events = {}
        self._containers = []

    def _getEpoll(self):
        if not self.__epoll:
            self.__epoll = select.epoll(self._sizehint)

        return self.__epoll

    def fileno(self):
        return self._getEpoll().fileno()

    def close(self):
        self.__epoll is not None and self.__epoll.close()

    def register(self, container, eventmask=INPUT|ERROR, trigger=None,
                 identifier=None):
        fd = container.fileno()
        self._queue[fd] = identifier is not None and identifier or container
        trigger = trigger and trigger or getattr(
            container, '__trigger__', self.LEVEL)
        self._getEpoll().register(fd, eventmask|(select.EPOLLET*trigger))

    def unregester(self, container):
        fd = container.fileno()
        self._getEpoll().unregester(fd)
        self._events.pop(fd, 0)
        return self._queue.pop(fd, 0)

    def eventWait(self, timeout=-1):
        readyEvents = self._getEpoll().poll(timeout, maxevents=len(self._queue))

        if readyEvents:
            self._events.update(dict(readyEvents))
            self._containers[:] = [c for fd, c in self._queue.items()
                                   if fd in self._events]

    def hasInput(self, container):
        return bool(self._events.get(container.fileno(), 0) & self.INPUT)

    def hasOutput(self, container):
        return bool(self._events.get(container.fileno(), 0) & self.OUTPUT)

    def hasError(self, container):
        return bool(self._events.get(container.fileno(), 0) & self.ERROR)

    def hasHangup(self, container):
        return bool(self._events.get(container.fileno(), 0) & self.HANGUP)

    def hasPriorityInput(self, container):
        return bool(self._events.get(container.fileno(), 0) & self.PRI_INPUT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
