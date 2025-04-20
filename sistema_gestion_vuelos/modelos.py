from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Vuelo(Base):
    __tablename__ = "vuelos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_vuelo = Column(String, unique=True, index=True)
    aerolinea = Column(String)
    origen = Column(String)
    destino = Column(String)
    hora_programada = Column(DateTime)
    es_emergencia = Column(Boolean, default=False)
    estado = Column(String)  # "programado", "abordando", "despegado", "cancelado", "retrasado"
    
    # Nueva columna para tracking de historial
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relación con el historial
    registros_historial = relationship("HistorialVuelo", back_populates="vuelo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Vuelo({self.numero_vuelo}, {self.aerolinea}, {self.origen}->{self.destino})"
    
    def a_diccionario(self):
        return {
            "id": self.id,
            "numero_vuelo": self.numero_vuelo,
            "aerolinea": self.aerolinea,
            "origen": self.origen,
            "destino": self.destino,
            "hora_programada": self.hora_programada.isoformat() if self.hora_programada else None,
            "es_emergencia": self.es_emergencia,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class HistorialVuelo(Base):
    """Tabla para mantener historial de cambios en vuelos"""
    __tablename__ = "historial_vuelos"
    
    id = Column(Integer, primary_key=True, index=True)
    vuelo_id = Column(Integer, ForeignKey("vuelos.id"))
    timestamp = Column(DateTime, default=datetime.now)
    estado_anterior = Column(String)
    estado_nuevo = Column(String)
    notas = Column(String, nullable=True)
    
    # Relación con vuelo
    vuelo = relationship("Vuelo", back_populates="registros_historial")
    
    def __repr__(self):
        return f"HistorialVuelo({self.vuelo_id}, {self.estado_anterior}->{self.estado_nuevo})"


class Aerolinea(Base):
    """Tabla de aerolíneas para normalizar los datos"""
    __tablename__ = "aerolineas"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)
    nombre = Column(String)
    pais_origen = Column(String)
    logo_url = Column(String, nullable=True)
    
    def __repr__(self):
        return f"Aerolinea({self.codigo}, {self.nombre})"


class Aeropuerto(Base):
    """Tabla de aeropuertos para normalizar los datos"""
    __tablename__ = "aeropuertos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_iata = Column(String(3), unique=True, index=True)
    nombre = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    
    def __repr__(self):
        return f"Aeropuerto({self.codigo_iata}, {self.nombre})"


# Configuración de la base de datos
URL_BASE_DE_DATOS = "sqlite:///./vuelos.db"
motor = create_engine(URL_BASE_DE_DATOS)
Base.metadata.create_all(bind=motor)
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)