# Importamos la clase principal de la interfaz desde el módulo gui
from gui.app import AplicacionParticionamiento

# Verificamos si este archivo se está ejecutando directamente
if __name__ == "__main__":
    # Instanciamos la aplicación de Tkinter
    app = AplicacionParticionamiento()
    # Iniciamos el bucle principal de la interfaz para que sea interactiva
    app.mainloop()