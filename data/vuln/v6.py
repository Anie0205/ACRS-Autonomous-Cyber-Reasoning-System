import subprocess
user = input()
subprocess.call("ping " + user, shell=True)
