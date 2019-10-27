def is_null(param):
    if param is None:
        return True
    if isinstance(param,str):
        if len(param.strip()) < 1:
            return True
    elif isinstance(param,(tuple,list)):
        if len(param) < 1:
            return True
    return False