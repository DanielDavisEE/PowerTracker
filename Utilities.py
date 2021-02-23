import logging

logging.basicConfig(level=logging.DEBUG)

def print_name(f):
    
    def inner(*args, **kwargs):
    
        logging.info(f"Function call: {f.__name__}")        
        f(*args, **kwargs)
        
    return inner