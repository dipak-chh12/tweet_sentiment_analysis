import logging
from collections import deque

def setup_logger(name, log_file='logs/app.log'):
    import os
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class RollingWindow:
    def __init__(self, maxlen=50):
        self.times = deque(maxlen=maxlen)
        self.values = deque(maxlen=maxlen)
    
    def append(self, time, value):
        self.times.append(time)
        self.values.append(value)
    
    def get_lists(self):
        return list(self.times), list(self.values)