import os
filename = input()
with open(filename, "x") as f:
    f.write("created")
