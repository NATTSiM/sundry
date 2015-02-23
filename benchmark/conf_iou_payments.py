workers = 1500
summary_file = '/home/mtravis/tmp/summary.log'
log_file = '/home/mtravis/tmp/out.log'
under_threshold = None
over_threshold = None
summary_interval = 10
rate = 5
# Ramp up time in seconds
ramp = 1
# For per-request host round-robin.
hosts = [ None ]
params = {'accounts_file': '/home/mtravis/tmp/fundaccounts.json',
          'timeout': 10,
          'hosts': [
              'http://wsttest6:51234',
              'http://wsttest7:51234',
              'http://wsttest8:51234',
              'http://wsttest9:51234'
          ]
}
