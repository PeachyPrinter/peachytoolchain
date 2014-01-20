import cProfile

class profile:
    def __init__(self, stats_filename):
        self.stats_filename = stats_filename

    def __call__(self, profile_func):
        def profile_wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            try:
                retval = profiler.runcall(profile_func, *args, **kwargs)
            finally:
                profiler.dump_stats(self.stats_filename)
                print('*** Profiling pstats saved to file "%s"' % (self.stats_filename,))
            return retval
        return profile_wrapper
