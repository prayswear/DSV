import logging

def log_init(filename):
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s',
                        datefmt='%d %b %Y %H:%M:%S', filename=filename, filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)