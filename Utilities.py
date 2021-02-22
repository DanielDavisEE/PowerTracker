import logging

logging.basicConfig(level=logging.DEBUG)

def print_name(f):
    
    def inner(*args):
    
        logging.info(f"Function call: {f.__name__}")        
        f(*args)
        
    return inner