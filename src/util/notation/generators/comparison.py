
def equals(val,attr_):
    def equals_lmbd(obj):
        return attr_(obj) == val

    return equals_lmbd