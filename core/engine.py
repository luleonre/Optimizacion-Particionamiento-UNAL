import numpy as np
from core.metrics import calcular_costo_corte

def resolver_exhaustivo(matriz, k):
    """Encuentra el óptimo global usando Backtracking iterativo."""
    n = len(matriz)
    mejor_costo = float('inf') # Inicializamos con infinito
    mejor_particion = None
    pila = [[]] # Pila (LIFO) para evitar recursión profunda
    
    while pila:
        estado_actual = pila.pop() # Sacamos el último estado explorado
        
        # Si ya asignamos todos los nodos a un grupo
        if len(estado_actual) == n:
            # Verificamos que realmente se hayan usado k grupos
            if len(set(estado_actual)) == k:
                costo = calcular_costo_corte(matriz, estado_actual)
                # Si el costo es menor al registrado, actualizamos el mejor
                if costo < mejor_costo:
                    mejor_costo = costo
                    mejor_particion = estado_actual
            continue
        
        # Generamos nuevas combinaciones agregando el nodo actual a cada grupo posible
        for grupo in range(k-1, -1, -1):
            pila.append(estado_actual + [grupo])
            
    return mejor_particion, mejor_costo

def resolver_heuristico(matriz, k):
    """Algoritmo Greedy para sistemas grandes (N >= 12)."""
    n = len(matriz)
    particion = [-1] * n # Inicializamos nodos sin grupo
    
    for i in range(n):
        mejor_costo_parcial = float('inf')
        mejor_grupo = 0
        
        # Probamos meter el nodo 'i' en cada uno de los k grupos
        for g in range(k):
            particion[i] = g
            costo_actual = 0
            # Calculamos el costo acumulado de las conexiones cortadas hasta ahora
            for u in range(i + 1):
                for v in range(u + 1, i + 1):
                    if particion[u] != particion[v]:
                        costo_actual += matriz[u][v]
            
            # Elegimos el grupo que genere menos costo localmente
            if costo_actual < mejor_costo_parcial:
                mejor_costo_parcial = costo_actual
                mejor_grupo = g
        
        # Asignamos definitivamente el nodo i al mejor grupo encontrado
        particion[i] = mejor_grupo
        
    return particion, calcular_costo_corte(matriz, particion)

def resolver_sistema(matriz, k):
    """Selecciona el algoritmo según el tamaño del sistema."""
    n = len(matriz)
    # Si el sistema es pequeño, garantizamos el óptimo con exhaustivo
    if n < 12:
        return resolver_exhaustivo(matriz, k)
    # Si es grande, usamos la heurística para evitar tiempos de espera infinitos
    else:
        return resolver_heuristico(matriz, k)