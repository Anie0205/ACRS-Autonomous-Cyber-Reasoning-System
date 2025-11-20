attr = input()
print(getattr(__import__("os"), attr))
