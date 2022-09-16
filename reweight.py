import ctypes
if __name__ == "__main__":
    a = 1024
    address = id(a)
    print(address)
    print(ctypes.cast(address, ctypes.py_object).value)
    


    print("+_I+")