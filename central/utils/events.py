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
        self._epoll = None
        self._queue = {}

    def _getEpoll(self):
        if not self._epoll:
            self._epoll = select.epoll(self._sizehint)

        return self._epoll

    def fileno(self):
        return self._getEpoll().fileno()

    def register(self, container, eventmask=INPUT|ERROR, trigger=None,
                 identifier=None):
        self._queue[fd] = identifier
        trigger = trigger and trigger or self.LEVEL
        self._getEpoll().register(container.fileno(), eventmask)

    def unregester(self, container):
        self._getEpoll().unregester(container.fileno())
