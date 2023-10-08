'''Routines for interfacing with CAS (i.e. Sympy) and other math libraries'''
import re

def create_safe_symbol(s):
    return s.replace('.', '__')

def recover_unsafe_symbol(s):
    return s.replace('__','.')

def adjust_set_membership_syntax(c):
    return c.replace("Contains", "in")

def revert_set_membership_syntax(c):
    return c.replace("in","Contains")

def create_safe_constraint(c):
    #split_chars = [" ", "(",")","+","-","*","/","{","}","$",""]
    c_splits = re.findall(r'[a-zA-Z0-9._]+|[^a-zA-Z0-9._]+', c)
    #c_splits=re.split(r'[^a-zA-Z0-9._]+', c)
    #c_splits=c.split(" ")
    c_safe=""

    for splt in c_splits:
        try:
            float(splt)
            c_safe = c_safe + splt
        except:
            c_safe = c_safe + create_safe_symbol(splt)

    return c_safe