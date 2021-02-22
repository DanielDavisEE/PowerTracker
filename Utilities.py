def print_name(f):
    
    def inner():
        print(f.__name__)
        f()
        
    return inner