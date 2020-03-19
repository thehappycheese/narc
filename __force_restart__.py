import os, sys

def force_restart():
    '''kill the current python process and replace it with a new one which has the same system arguments (sys.argv)'''
    python = sys.executable
    os.execl(python, python, * (sys.argv)) # replaces the current process with this new one