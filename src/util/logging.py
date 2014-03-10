import datetime
import os

class Logging(object):
    LEVELS =  ['trace', 'debug', 'info', 'warning','error' ] 
    _levels = [] 

    def __init__(self, level = 'default'):
        level = level.lower()
        if level == 'default':
            level = os.getenv('LOG_LEVEL', 'warning')
        if level not in self.LEVELS:
            raise Exception("Logging level of %s invalid use: %s" % (level, self.LEVELS))
        self._levels = self.LEVELS[self.LEVELS.index(level):]

    def trace(self, statement):
        self._log("TRACE", statement)

    def debug(self, statement):
        self._log("DEBUG", statement)

    def info(self, statement):
        self._log('INFO', statement)

    def warning(self, statement):
        self._log('WARNING', statement)
    
    def error(self, statement):
        self._log('ERROR', statement)

    def _log(self, level, statement):
        if level.lower() in self._levels:
            print('%s - %s: %s' % ( self._now(), level, statement) )

    def _now(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')