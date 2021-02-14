with open("PowerTrackerGUI.py") as f:
    #code = compile(f.read(), "somefile.py", 'exec')
    #exec(code, global_vars, local_vars)
    exec(f.read())