#
# central/utils/logging_config.py
#

"""
The ConfigLogger class is used to configure loggers.

by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import logging


def getBasePath():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class ConfigLogger(object):
    """
    Setup some basic logging. This could get more sophisticated in the future.
    """
    _DEFAULT_FORMAT = ("%(asctime)s %(levelname)s %(module)s %(funcName)s "
                       "[line:%(lineno)d] %(message)s")

    def __init__(self, logPath=None):
        if logPath:
            self._logPath = logPath.rstrip('/')

        self._format = self._DEFAULT_FORMAT

    def config(self, loggerName, filename=None, level=logging.INFO):
        """
        loggerName is not used yet.
        """
        if filename is not None:
            filePath = os.path.join(self._logPath, filename)
        else:
            filePath = None

        return logging.basicConfig(filename=filePath, format=self._format,
                                   level=level)


    def setFormat(self, fmt=None, default=_DEFAULT_FORMAT):
        """
        Must be called before the config method or it will have no effect.
        """
        if not fmt: fmt = default
        self._format = fmt
