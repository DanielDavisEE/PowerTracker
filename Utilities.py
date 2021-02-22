import logging

logging.basicConfig(level=logging.DEBUG)

def print_name(f):
    
    def inner():
    
        logging.info(f"Function call: {f.__name__}")        
        print(f.__name__)
        f()
        
    return inner