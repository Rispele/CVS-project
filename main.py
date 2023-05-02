import DiffTool as dt

differ = dt.DiffTool()

a = ['a', 'b', 'c', 'd', 'e']
b = ['a', 'f', 'c', 'd', 'e']

for i in differ.difference(a, b):
    print(i)