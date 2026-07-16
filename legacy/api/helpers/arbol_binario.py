class Nodo:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class ArbolBinarioBusqueda:
    def __init__(self):
        self.root = None

    def insertar(self, key, value):
        if self.root is None:
            self.root = Nodo(key, value)
        else:
            self._insertar_recursivo(self.root, key, value)

    def _insertar_recursivo(self, nodo, key, value):
        if key < nodo.key:
            if nodo.left is None:
                nodo.left = Nodo(key, value)
            else:
                self._insertar_recursivo(nodo.left, key, value)
        elif key > nodo.key:
            if nodo.right is None:
                nodo.right = Nodo(key, value)
            else:
                self._insertar_recursivo(nodo.right, key, value)
        else:
            print(f"Clave duplicada: {key}. No se puede insertar.")

    def buscar(self, key):
        return self._buscar_recursivo(self.root, key)

    def _buscar_recursivo(self, nodo, key):
        if nodo is None:
            return None
        if key == nodo.key:
            return nodo.value
        elif key < nodo.key:
            return self._buscar_recursivo(nodo.left, key)
        else:
            return self._buscar_recursivo(nodo.right, key)
