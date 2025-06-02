
#arreglo 
#buscar dentro del array los numeros que sumados den 7


arrgelo  = [4, 5, 9, 0, 1, 2, 3, 6]

numeros = []

for i, v in enumerate(arrgelo):
    for k, j in enumerate(arrgelo):
        if  (j + v) == 7:
            numeros.append(j)
            numeros.append(v)
            print(v, j) 

print(numeros)




