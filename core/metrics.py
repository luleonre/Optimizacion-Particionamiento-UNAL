def calcular_costo_corte(matriz, particion):
    """
    Función de evaluación: Suma los pesos de todas las aristas
    cuyos nodos extremos pertenecen a diferentes grupos (corte).
    """
    n = len(matriz)
    costo = 0
    # Recorremos solo la mitad superior de la matriz para evitar duplicar la suma
    for i in range(n):
        for j in range(i + 1, n):
            # Si el grupo del nodo 'i' es diferente al grupo del nodo 'j'
            if particion[i] != particion[j]:
                # Sumamos el peso de la conexión como 'pérdida'
                costo += matriz[i][j]
    return costo