class Nodo:
    """Nodo para la lista doblemente enlazada"""
    
    def __init__(self, vuelo):
        self.vuelo = vuelo  # Objeto Vuelo de SQLAlchemy
        self.siguiente = None
        self.anterior = None


class ListaDoblementeEnlazada:
    """Implementación de una lista doblemente enlazada para gestionar vuelos"""
    
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamanio = 0
    
    def insertar_al_frente(self, vuelo):
        """Añade un vuelo al inicio de la lista (para emergencias)"""
        nuevo_nodo = Nodo(vuelo)
        
        if self.cabeza is None:
            # Lista vacía
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            # Lista no vacía
            nuevo_nodo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo_nodo
            self.cabeza = nuevo_nodo
        
        self.tamanio += 1
        return nuevo_nodo
    
    def insertar_al_final(self, vuelo):
        """Añade un vuelo al final de la lista (vuelos regulares)"""
        nuevo_nodo = Nodo(vuelo)
        
        if self.cola is None:
            # Lista vacía
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            # Lista no vacía
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        
        self.tamanio += 1
        return nuevo_nodo
    
    def obtener_primero(self):
        """Retorna (sin remover) el primer vuelo de la lista"""
        if self.cabeza is None:
            return None
        return self.cabeza.vuelo
    
    def obtener_ultimo(self):
        """Retorna (sin remover) el último vuelo de la lista"""
        if self.cola is None:
            return None
        return self.cola.vuelo
    
    def longitud(self):
        """Retorna el número total de vuelos en la lista"""
        return self.tamanio
    
    def _obtener_nodo_en_posicion(self, posicion):
        """Método auxiliar para obtener el nodo en una posición específica"""
        if posicion < 0 or posicion >= self.tamanio:
            raise IndexError("Posición fuera de rango")
        
        if posicion <= self.tamanio // 2:
            # Buscar desde el inicio
            actual = self.cabeza
            for _ in range(posicion):
                actual = actual.siguiente
        else:
            # Buscar desde el final
            actual = self.cola
            for _ in range(self.tamanio - 1 - posicion):
                actual = actual.anterior
        
        return actual
    
    def insertar_en_posicion(self, vuelo, posicion):
        """Inserta un vuelo en una posición específica"""
        if posicion < 0 or posicion > self.tamanio:
            raise IndexError("Posición fuera de rango")
        
        if posicion == 0:
            return self.insertar_al_frente(vuelo)
        elif posicion == self.tamanio:
            return self.insertar_al_final(vuelo)
        else:
            nuevo_nodo = Nodo(vuelo)
            actual = self._obtener_nodo_en_posicion(posicion)
            
            # Insertar antes de actual
            nuevo_nodo.siguiente = actual
            nuevo_nodo.anterior = actual.anterior
            actual.anterior.siguiente = nuevo_nodo
            actual.anterior = nuevo_nodo
            
            self.tamanio += 1
            return nuevo_nodo
    
    def extraer_de_posicion(self, posicion):
        """Remueve y retorna el vuelo en la posición dada"""
        if posicion < 0 or posicion >= self.tamanio:
            raise IndexError("Posición fuera de rango")
        
        if posicion == 0:
            # Extraer el primer elemento
            if self.cabeza is None:
                return None
            
            vuelo = self.cabeza.vuelo
            self.cabeza = self.cabeza.siguiente
            
            if self.cabeza is None:
                self.cola = None
            else:
                self.cabeza.anterior = None
            
            self.tamanio -= 1
            return vuelo
        
        elif posicion == self.tamanio - 1:
            # Extraer el último elemento
            vuelo = self.cola.vuelo
            self.cola = self.cola.anterior
            
            if self.cola is None:
                self.cabeza = None
            else:
                self.cola.siguiente = None
            
            self.tamanio -= 1
            return vuelo
        
        else:
            # Extraer de una posición intermedia
            actual = self._obtener_nodo_en_posicion(posicion)
            vuelo = actual.vuelo
            
            # Actualizar enlaces
            actual.anterior.siguiente = actual.siguiente
            actual.siguiente.anterior = actual.anterior
            
            self.tamanio -= 1
            return vuelo
    
    def listar_todos(self):
        """Devuelve una lista con todos los vuelos en la lista enlazada"""
        vuelos = []
        actual = self.cabeza
        while actual:
            vuelos.append(actual.vuelo)
            actual = actual.siguiente
        return vuelos
    
    # MEJORAS
    
    def buscar_por_numero_de_vuelo(self, numero_vuelo):
        """Busca un vuelo por su número y retorna su posición y el nodo"""
        actual = self.cabeza
        posicion = 0
        
        while actual:
            if actual.vuelo.numero_vuelo == numero_vuelo:
                return posicion, actual
            actual = actual.siguiente
            posicion += 1
            
        return -1, None
    
    def invertir_lista(self):
        """Invierte el orden de la lista completa (útil para ciertos reportes)"""
        if self.cabeza is None or self.cabeza == self.cola:
            return  # Lista vacía o con un solo elemento
            
        actual = self.cabeza
        self.cola = self.cabeza  # El que era primero será último
        
        prev = None
        while actual:
            siguiente = actual.siguiente
            actual.siguiente = prev
            actual.anterior = siguiente
            prev = actual
            actual = siguiente
            
        self.cabeza = prev  # El que era último será primero
    
    def filtrar_por_estado(self, estado):
        """Devuelve una lista con todos los vuelos en un estado específico"""
        vuelos_filtrados = []
        actual = self.cabeza
        
        while actual:
            if actual.vuelo.estado == estado:
                vuelos_filtrados.append(actual.vuelo)
            actual = actual.siguiente
            
        return vuelos_filtrados
    
    def intercambiar_nodos(self, posicion1, posicion2):
        """Intercambia dos nodos en la lista por sus posiciones"""
        if posicion1 == posicion2:
            return
            
        if posicion1 < 0 or posicion1 >= self.tamanio or posicion2 < 0 or posicion2 >= self.tamanio:
            raise IndexError("Posición fuera de rango")
            
        # Asegurar que posicion1 < posicion2
        if posicion1 > posicion2:
            posicion1, posicion2 = posicion2, posicion1
            
        # Obtener nodos
        nodo1 = self._obtener_nodo_en_posicion(posicion1)
        nodo2 = self._obtener_nodo_en_posicion(posicion2)
        
        # Casos especiales
        es_adyacente = (posicion1 + 1 == posicion2)
        es_cabeza = (posicion1 == 0)
        es_cola = (posicion2 == self.tamanio - 1)
        
        # Guardamos referencias a los nodos adyacentes
        prev1 = nodo1.anterior
        next1 = nodo1.siguiente
        prev2 = nodo2.anterior
        next2 = nodo2.siguiente
        
        # Actualizar cabeza/cola si es necesario
        if es_cabeza:
            self.cabeza = nodo2
        if es_cola:
            self.cola = nodo1
            
        # Actualizar enlaces
        if es_adyacente:
            # Nodos adyacentes
            nodo1.siguiente = next2
            nodo1.anterior = nodo2
            nodo2.siguiente = nodo1
            nodo2.anterior = prev1
            
            if prev1:
                prev1.siguiente = nodo2
            if next2:
                next2.anterior = nodo1
        else:
            # Nodos no adyacentes
            nodo1.siguiente = next2
            nodo1.anterior = prev2
            nodo2.siguiente = next1
            nodo2.anterior = prev1
            
            if prev1:
                prev1.siguiente = nodo2
            if next1:
                next1.anterior = nodo2
            if prev2:
                prev2.siguiente = nodo1
            if next2:
                next2.anterior = nodo1