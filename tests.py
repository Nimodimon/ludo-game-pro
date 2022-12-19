a = [1, 2, 3, 4]
b = [5, 4, 3, 2]

def change_turn():
    global a, b
    a, b = b, a

change_turn()

print(a)
print(b)
