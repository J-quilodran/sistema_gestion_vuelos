from modelos import Vuelo
from lista_doblemente_enlazada import ListaDoblementeEnlazada
from sqlalchemy import and_

class GestorVuelos:
    """Clase para gestionar los vuelos utilizando la lista doblemente enlazada y la base de datos"""
    
    def __init__(self, sesion_db):
        self.lista_vuelos = ListaDoblementeEnlazada()
        self.sesion_db = sesion_db
        
        # Cargar vuelos existentes de la base de datos
        self._cargar_desde_base_de_datos()
    
    def _cargar_desde_base_de_datos(self):
        """Carga los vuelos desde la base de datos a la lista enlazada"""
        vuelos = self.sesion_db.query(Vuelo).order_by(Vuelo.hora_programada).all()
        
        # Primero cargar los vuelos de emergencia
        for vuelo in vuelos:
            if vuelo.es_emergencia:
                self.lista_vuelos.insertar_al_frente(vuelo)
            else:
                self.lista_vuelos.insertar_al_final(vuelo)
    
    def agregar_vuelo(self, datos_vuelo):
        """Agrega un nuevo vuelo a la lista y a la base de datos"""
        # Crear nuevo vuelo en la base de datos
        nuevo_vuelo = Vuelo(**datos_vuelo)
        self.sesion_db.add(nuevo_vuelo)
        self.sesion_db.commit()
        self.sesion_db.refresh(nuevo_vuelo)
        
        # Agregar a la lista enlazada según si es emergencia o no
        if nuevo_vuelo.es_emergencia:
            self.lista_vuelos.insertar_al_frente(nuevo_vuelo)
        else:
            self.lista_vuelos.insertar_al_final(nuevo_vuelo)
        
        return nuevo_vuelo
    
    def obtener_todos_los_vuelos(self):
        """Retorna todos los vuelos en la lista enlazada"""
        return self.lista_vuelos.listar_todos()
    
    def obtener_vuelo_por_id(self, id_vuelo):
        """Busca un vuelo por su ID"""
        return self.sesion_db.query(Vuelo).filter(Vuelo.id == id_vuelo).first()
    
    def obtener_primer_vuelo(self):
        """Retorna el primer vuelo de la lista"""
        return self.lista_vuelos.obtener_primero()
    
    def obtener_ultimo_vuelo(self):
        """Retorna el último vuelo de la lista"""
        return self.lista_vuelos.obtener_ultimo()
    
    def insertar_vuelo_en_posicion(self, datos_vuelo, posicion):
        """Inserta un vuelo en una posición específica"""
        # Crear nuevo vuelo en la base de datos
        nuevo_vuelo = Vuelo(**datos_vuelo)
        self.sesion_db.add(nuevo_vuelo)
        self.sesion_db.commit()
        self.sesion_db.refresh(nuevo_vuelo)
        
        # Insertar en la posición indicada
        self.lista_vuelos.insertar_en_posicion(nuevo_vuelo, posicion)
        return nuevo_vuelo
    
    def eliminar_vuelo_en_posicion(self, posicion):
        """Remueve un vuelo de una posición específica"""
        vuelo = self.lista_vuelos.extraer_de_posicion(posicion)
        if vuelo:
            # Actualizar en la base de datos (por ejemplo, marcar como cancelado)
            vuelo.estado = "cancelado"
            self.sesion_db.commit()
        return vuelo
    
    def actualizar_vuelo(self, id_vuelo, datos_vuelo):
        """Actualiza la información de un vuelo"""
        vuelo = self.sesion_db.query(Vuelo).filter(Vuelo.id == id_vuelo).first()
        if not vuelo:
            return None
        
        # Actualizar atributos
        for clave, valor in datos_vuelo.items():
            setattr(vuelo, clave, valor)
        
        self.sesion_db.commit()
        
        # Como la posición puede haber cambiado, reconstruimos la lista
        self.lista_vuelos = ListaDoblementeEnlazada()
        self._cargar_desde_base_de_datos()
        
        return vuelo
    
    # MEJORAS
    
    def longitud(self):
        """Retorna el número total de vuelos en la lista"""
        return self.lista_vuelos.longitud()
    
    def obtener_vuelos_por_estado(self, estado):
        """Retorna todos los vuelos con un estado específico"""
        vuelos = self.sesion_db.query(Vuelo).filter(Vuelo.estado == estado).all()
        return vuelos
    
    def obtener_vuelos_por_aerolinea(self, aerolinea):
        """Retorna todos los vuelos de una aerolínea específica"""
        vuelos = self.sesion_db.query(Vuelo).filter(Vuelo.aerolinea == aerolinea).all()
        return vuelos
    
    def obtener_vuelos_por_origen_destino(self, origen=None, destino=None):
        """Retorna los vuelos filtrados por origen y/o destino"""
        filtros = []
        if origen:
            filtros.append(Vuelo.origen == origen)
        if destino:
            filtros.append(Vuelo.destino == destino)
            
        if filtros:
            vuelos = self.sesion_db.query(Vuelo).filter(and_(*filtros)).all()
            return vuelos
        return []
    
    def reordenar_vuelos_por_retrasos(self):
        """Reordena los vuelos basados en retrasos (los retrasados al final)"""
        # Obtener todos los vuelos
        todos_vuelos = self.lista_vuelos.listar_todos()
        
        # Crear una nueva lista ordenada
        self.lista_vuelos = ListaDoblementeEnlazada()
        
        # Primero agregar emergencias
        for vuelo in todos_vuelos:
            if vuelo.es_emergencia and vuelo.estado != "retrasado":
                self.lista_vuelos.insertar_al_frente(vuelo)
        
        # Luego agregar vuelos normales no retrasados
        for vuelo in todos_vuelos:
            if not vuelo.es_emergencia and vuelo.estado != "retrasado":
                self.lista_vuelos.insertar_al_final(vuelo)
        
        # Finalmente agregar vuelos retrasados (al final)
        for vuelo in todos_vuelos:
            if vuelo.estado == "retrasado":
                self.lista_vuelos.insertar_al_final(vuelo)
                
        return self.lista_vuelos.listar_todos()
    
    def buscar_vuelo_por_numero(self, numero_vuelo):
        """Busca un vuelo por su número de vuelo"""
        return self.sesion_db.query(Vuelo).filter(Vuelo.numero_vuelo == numero_vuelo).first()