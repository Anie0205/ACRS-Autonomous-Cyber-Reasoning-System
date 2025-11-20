import os
filename = input()
if not os.path.exists(filename):
    open(filename, "w").write("created")
