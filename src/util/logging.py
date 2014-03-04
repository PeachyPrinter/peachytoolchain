import datetime

class Logging(object):
    levels = ['trace', 'info', 'warning','error' ] 

    def __init__(self, level = "error"):
        self.level = level.lower()
        if self.level not in self.levels:
            raise Exception("Logging level of % invalid use: %s" % (level, levels))

    def info(self, statement):
        self._log('INFO', statement)

    def warning(self, statement):
        self._log('WARNING', statement)
    
    def error(self, statement):
        self._log('ERROR', statement)

    def trace(self, statement):
        self._log("TRACE", statement)

    def _log(self, level, statement):
        print('%s - %s: %s' % ( self._now(), level, statement) )

    def _now(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')