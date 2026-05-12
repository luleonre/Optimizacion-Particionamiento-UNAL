import pandas as pd
import numpy as np

def cargar_matriz_csv(ruta_archivo):
    try:
        # Leemos el CSV usando la primera columna como índice de nombres
        df = pd.read_csv(ruta_archivo, index_col=0)
        # Convertimos el DataFrame de pandas a una matriz numérica de NumPy
        matriz = df.to_numpy()
        # Extraemos los nombres de las columnas para etiquetar los servicios
        nombres = df.columns.tolist()
        
        # Validación: El sistema requiere que la matriz sea cuadrada (nodos x nodos)
        n, m = matriz.shape
        if n != m:
            raise ValueError(f"La matriz no es cuadrada. Dimensiones: {n}x{m}")
        
        # Validación: No pueden existir dependencias negativas
        if (matriz < 0).any():
            raise ValueError("La matriz contiene valores negativos de dependencia.")
        
        # Validación: En grafos no dirigidos, la relación i->j debe ser igual a j->i
        if not np.allclose(matriz, matriz.T):
            raise ValueError("La matriz no es simétrica (D[i,j] != D[j,i]).")
            
        return matriz, nombres
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    except Exception as e:
        raise Exception(f"Error inesperado al cargar el archivo: {str(e)}")