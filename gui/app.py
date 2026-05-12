import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from core.loader import cargar_matriz_csv
from core.engine import resolver_sistema

class AplicacionParticionamiento(tk.Tk):
    def __init__(self):
        super().__init__()
        # Configuración básica de la ventana principal
        self.title("Optimización de Particionamiento - UNAL")
        self.geometry("900x750")
        
        # Variables de estado del sistema
        self.matriz = None
        self.nombres = None
        self.nodos_graficos = [] # Almacena coordenadas (x,y) del Canvas
        self.aristas_graficas = [] # Almacena conexiones hechas a mano
        self.nodo_origen = None # Para el proceso de conectar dos nodos
        
        # Creación de pestañas (Tabs)
        self.tabs = ttk.Notebook(self)
        self.tab_archivo = ttk.Frame(self.tabs)
        self.tab_dibujo = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_archivo, text="Cargar CSV")
        self.tabs.add(self.tab_dibujo, text="Dibujar Grafo")
        self.tabs.pack(expand=1, fill="both")
        
        # Configuración de contenidos de pestañas
        self._setup_tab_archivo()
        self._setup_tab_dibujo()
        
        # Consola de salida de texto para resultados numéricos
        self.txt_resultados = tk.Text(self, height=10, bg="#2b2b2b", fg="#ffffff", font=("Consolas", 10))
        self.txt_resultados.pack(fill="x", padx=10, pady=10)

    def _setup_tab_archivo(self):
        """Configura la interfaz para carga de archivos CSV."""
        tk.Label(self.tab_archivo, text="Entrada por Archivo", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Button(self.tab_archivo, text="Cargar CSV", command=self.cargar_archivo, bg="#4CAF50", fg="white").pack(pady=5)
        self.lbl_info = tk.Label(self.tab_archivo, text="Ningún archivo cargado")
        self.lbl_info.pack()
        tk.Label(self.tab_archivo, text="Número de particiones (k):").pack()
        self.ent_k_file = tk.Entry(self.tab_archivo)
        self.ent_k_file.pack()
        tk.Button(self.tab_archivo, text="Ejecutar Algoritmo", command=lambda: self.ejecutar("archivo"), bg="#2196F3", fg="white").pack(pady=10)

    def _setup_tab_dibujo(self):
        """Configura el lienzo de dibujo interactivo."""
        instrucciones = "INSTRUCCIONES: Click izquierdo (Crear Nodo) | Click derecho (Conectar Nodos)"
        tk.Label(self.tab_dibujo, text=instrucciones, font=("Arial", 9, "italic")).pack(pady=5)
        self.canvas = tk.Canvas(self.tab_dibujo, bg="white", height=400)
        self.canvas.pack(fill="both", expand=True, padx=10)
        # Bind de click izquierdo para crear nodos
        self.canvas.bind("<Button-1>", self.crear_nodo)
        
        # Controles inferiores del Canvas
        ctrl_frame = tk.Frame(self.tab_dibujo)
        ctrl_frame.pack(pady=10)
        tk.Label(ctrl_frame, text="k:").pack(side="left")
        self.ent_k_draw = tk.Entry(ctrl_frame, width=5)
        self.ent_k_draw.pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Limpiar", command=self.limpiar_dibujo).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Procesar Grafo", command=lambda: self.ejecutar("dibujo"), bg="#2196F3", fg="white").pack(side="left")

    def crear_nodo(self, event):
        """Crea un círculo en el Canvas y lo registra como nodo."""
        x, y = event.x, event.y
        nombre = f"S{len(self.nodos_graficos)}" # Nombre automático S0, S1...
        self.nodos_graficos.append((x, y, nombre))
        idx = len(self.nodos_graficos) - 1
        r = 15
        # Dibujamos el círculo
        circulo = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#deff9a", outline="black", tags=("nodo", f"n_{idx}"))
        self.canvas.create_text(x, y, text=nombre, tags=("texto", f"t_{idx}"))
        # Asignamos click derecho al nodo para iniciar una conexión
        self.canvas.tag_bind(circulo, "<Button-3>", lambda e, i=idx: self.conectar_nodos(i))

    def conectar_nodos(self, idx):
        """Gestiona la lógica de conectar dos nodos con un peso."""
        if self.nodo_origen is None:
            # Primer nodo seleccionado
            self.nodo_origen = idx
            self.canvas.itemconfig(f"n_{idx}", fill="yellow") # Marcamos selección
        else:
            # Segundo nodo seleccionado
            if self.nodo_origen != idx:
                # Pedimos el peso de la arista al usuario
                peso = simpledialog.askinteger("Peso", "Peso de conexión:", minvalue=1)
                if peso:
                    self.aristas_graficas.append((self.nodo_origen, idx, peso))
                    # Dibujamos la línea de conexión
                    x1, y1, _ = self.nodos_graficos[self.nodo_origen]
                    x2, y2, _ = self.nodos_graficos[idx]
                    self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=str(peso), fill="red")
            # Restauramos el color original
            self.canvas.itemconfig(f"n_{self.nodo_origen}", fill="#deff9a")
            self.nodo_origen = None

    def limpiar_dibujo(self):
        """Resetea el área de dibujo."""
        self.canvas.delete("all")
        self.nodos_graficos = []
        self.aristas_graficas = []
        self.nodo_origen = None

    def cargar_archivo(self):
        """Abre el diálogo de archivos y carga la matriz desde CSV."""
        ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if ruta:
            self.matriz, self.nombres = cargar_matriz_csv(ruta)
            self.lbl_info.config(text=f"Cargado: {ruta.split('/')[-1]}")

    def ejecutar(self, modo):
        """Controlador que dispara el motor de resolución y muestra resultados."""
        try:
            if modo == "dibujo":
                n = len(self.nodos_graficos)
                if n == 0: return
                # Convertimos el dibujo a una matriz de adyacencia real
                self.matriz = np.zeros((n, n))
                for u, v, w in self.aristas_graficas:
                    self.matriz[u][v] = self.matriz[v][u] = w
                self.nombres = [n[2] for n in self.nodos_graficos]
                k = int(self.ent_k_draw.get())
            else:
                k = int(self.ent_k_file.get())
            
            # Llamamos al motor lógico
            particion, costo = resolver_sistema(self.matriz, k)
            
            # Mostramos resultados en la consola de la GUI
            self.txt_resultados.delete("1.0", tk.END)
            self.txt_resultados.insert(tk.END, f">>> VALOR DE PÉRDIDA (COSTO TOTAL): {costo}\n")
            self.txt_resultados.insert(tk.END, f">>> PARTES GENERADAS: {k}\n")
            self.txt_resultados.insert(tk.END, "="*40 + "\n")
            
            # Agrupamos nombres para mostrarlos por partición
            grupos = {}
            for i, p in enumerate(particion):
                if p not in grupos: grupos[p] = []
                grupos[p].append(self.nombres[i])
            for g, nodos in grupos.items():
                self.txt_resultados.insert(tk.END, f"PARTICIÓN {g}: {', '.join(nodos)}\n")
            
            # Lanzamos la visualización de Matplotlib
            self.visualizar_graficamente(particion, costo)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def visualizar_graficamente(self, particion, costo):
        """Genera el diagrama de grafos coloreado."""
        G = nx.from_numpy_array(self.matriz)
        plt.figure("Resultado de Particionamiento", figsize=(10, 6))
        # Paleta de colores para los grupos
        colores = ['#ff4d4d', '#4dff4d', '#4d4dff', '#ffff4d', '#ff4dff', '#4dffff']
        node_colors = [colores[p % len(colores)] for p in particion]
        
        # Calculamos la posición de los nodos (layout de resortes)
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, labels={i: self.nombres[i] for i in range(len(self.nombres))},
                node_color=node_colors, node_size=1500, font_size=10, font_weight="bold")
        
        plt.title(f"Visualización del Corte\nCosto de Pérdida: {costo}")
        plt.show()