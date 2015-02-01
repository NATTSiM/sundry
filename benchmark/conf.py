workers = 5000
summary_file = 'summary.log'
log_file = 'out.log'
under_threshold = None
over_threshold = None
summary_interval = 10
rate = 5
# thread stack size in KB
stack_size = 128
# ramp up time in seconds
ramp = 1
hosts = [
    'http://dfw10:7111',
    'http://dfw10:7112',
    'http://dfw10:7113',
    'http://dfw10:7114',
    'http://dfw10:7115',
    'http://dfw10:7116',
    'http://dfw10:7117',
    'http://dfw10:7118',
    'http://dfw10:7119',
    'http://dfw10:7120',
    'http://dfw10:7121',
    'http://dfw10:7122',
]
params = {'accounts_file': '/tmp/accounts.txt', 'timeout': 10}
