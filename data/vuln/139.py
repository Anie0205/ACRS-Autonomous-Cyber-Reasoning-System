
f = input()
with open("uploads/" + f, "rb") as fp:
    print(fp.read())
