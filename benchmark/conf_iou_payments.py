workers = 1500
summary_file = '/home/mtravis/res/summary.log'
log_file = '/home/mtravis/res/out.log'
under_threshold = None
over_threshold = None
summary_interval = 10
rate = 90
# Ramp up time in seconds
ramp = 60
# For per-request host round-robin.
hosts = [ None ]
params = {'accounts_file': '/home/mtravis/res/fundaccounts.json',
          'timeout': 10,
          'clients': 1,
          'instance': 0,
          'rsign': './scripts/rsign',
          'hosts': [
              'http://nyc-bm6-private:51234',
#              'http://nyc-bm6-private:52234',
#              'http://nyc-bm6-private:53234',
#              'http://nyc-bm6-private:54234',
              'http://nyc-bm7-private:51234',
#              'http://nyc-bm7-private:52234',
#              'http://nyc-bm7-private:53234',
#              'http://nyc-bm7-private:54234',
              'http://nyc-bm8-private:51234',
#              'http://nyc-bm8-private:52234',
#              'http://nyc-bm8-private:53234',
#              'http://nyc-bm8-private:54234',
#              'http://nyc-bm9-private:51234',
#              'http://nyc-bm9-private:52234',
#              'http://nyc-bm9-private:53234',
          ]
}
