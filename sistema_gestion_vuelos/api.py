from fastapi import FastAPI, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from modelos import SesionLocal, Vuelo
from gestor_vuelos import GestorVuelos
from pydantic import BaseModel, field_validator

class RespuestaConteo(BaseModel):
    total: int

class CrearVuelo(BaseModel):
    numero_vuelo: str
    aerolinea: str
    origen: str
    destino: str
    hora_programada: datetime
    es_emergencia: bool = False
    estado: str = "programado"
    
    @field_validator('numero_vuelo')
    @classmethod
    def validar_numero_vuelo(cls, v):
        # Validación de formato básico (2 letras seguidas de 3-4 números)
        import re
        if not re.match(r'^[A-Z]{2}\d{3,4}$', v):
            raise ValueError('Número de vuelo inválido. Debe tener formato: XX999 o XX9999')
        return v
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        estados_validos = ["programado", "abordando", "despegado", "retrasado", "cancelado"]
        if v not in estados_validos:
            raise ValueError(f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}')
        return v

class ActualizarVuelo(BaseModel):
    numero_vuelo: Optional[str] = None
    aerolinea: Optional[str] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    hora_programada: Optional[datetime] = None
    es_emergencia: Optional[bool] = None
    estado: Optional[str] = None
    
    @field_validator('numero_vuelo')
    @classmethod
    def validar_numero_vuelo(cls, v):
        if v is not None:
            import re
            if not re.match(r'^[A-Z]{2}\d{3,4}$', v):
                raise ValueError('Número de vuelo inválido. Debe tener formato: XX999 o XX9999')
        return v
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        if v is not None:
            estados_validos = ["programado", "abordando", "despegado", "retrasado", "cancelado"]
            if v not in estados_validos:
                raise ValueError(f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}')
        return v
class RespuestaVuelo(BaseModel):
    id: int
    numero_vuelo: str
    aerolinea: str
    origen: str
    destino: str
    hora_programada: datetime
    es_emergencia: bool
    estado: str

    class Config:
        from_attributes = True

class MensajeRespuesta(BaseModel):
    mensaje: str

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Gestión de Vuelos", 
    description="API REST para la gestión de vuelos en aeropuertos usando una lista doblemente enlazada",
    version="2.0.0"
)

# Dependencia para obtener la sesión de la base de datos
def obtener_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()
    
# Dependencia para obtener el gestor de vuelos
def obtener_gestor_vuelos(db: Session = Depends(obtener_db)):
    return GestorVuelos(db)
@app.post("/vuelos/", response_model=RespuestaVuelo, status_code=status.HTTP_201_CREATED, 
         summary="Crear un nuevo vuelo",
         description="Añade un nuevo vuelo al sistema. Los vuelos de emergencia se colocan al inicio de la lista.")
def crear_vuelo(vuelo: CrearVuelo, gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    # Verificar si ya existe un vuelo con ese número
    existente = gestor.buscar_vuelo_por_numero(vuelo.numero_vuelo)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un vuelo con el número {vuelo.numero_vuelo}"
        )
    return gestor.agregar_vuelo(vuelo.dict())

@app.get("/vuelos/", response_model=List[RespuestaVuelo],
        summary="Obtener todos los vuelos",
        description="Retorna una lista con todos los vuelos en el sistema.")
def leer_vuelos(
    skip: int = Query(0, description="Número de registros a saltar (para paginación)"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    gestor: GestorVuelos = Depends(obtener_gestor_vuelos)
):
    vuelos = gestor.obtener_todos_los_vuelos()
    return vuelos[skip:skip+limit]

@app.get("/vuelos/total", response_model=RespuestaConteo,
         summary="Total de vuelos",
         description="Retorna el número total de vuelos en el sistema.")
def obtener_total_vuelos(gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    valor = gestor.longitud()
    print(f"Valor: {valor}, Tipo: {type(valor)}")
    return {"total": valor}

@app.get("/vuelos/{id_vuelo}", response_model=RespuestaVuelo,
         summary="Obtener un vuelo por ID",
         description="Retorna un vuelo específico buscado por su ID.")
def leer_vuelo(id_vuelo: int, gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    vuelo = gestor.obtener_vuelo_por_id(id_vuelo)
    if vuelo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return vuelo

@app.put("/vuelos/{id_vuelo}", response_model=RespuestaVuelo,
         summary="Actualizar un vuelo",
         description="Actualiza la información de un vuelo existente.")
def actualizar_vuelo(id_vuelo: int, vuelo: ActualizarVuelo, gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    vuelo_actualizado = gestor.actualizar_vuelo(id_vuelo, vuelo.dict(exclude_unset=True))
    if vuelo_actualizado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return vuelo_actualizado


@app.delete("/vuelos/{id_vuelo}", response_model=RespuestaVuelo,
           summary="Eliminar un vuelo",
           description="Elimina un vuelo del sistema (lo marca como cancelado).")
def eliminar_vuelo(id_vuelo: int, gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    # Primero encontramos la posición del vuelo en la lista
    vuelos = gestor.obtener_todos_los_vuelos()
    posicion = None
    
    for i, vuelo in enumerate(vuelos):
        if vuelo.id == id_vuelo:
            posicion = i
            break
    
    if posicion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    
    return gestor.eliminar_vuelo_en_posicion(posicion)

@app.post("/vuelos/posicion/{posicion}", response_model=RespuestaVuelo,
          summary="Insertar vuelo en posición específica",
          description="Inserta un nuevo vuelo en una posición específica de la lista.")
def insertar_vuelo_en_posicion(posicion: int, vuelo: CrearVuelo, gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    try:
        return gestor.insertar_vuelo_en_posicion(vuelo.dict(), posicion)
    except IndexError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Posición fuera de rango")

@app.get("/vuelos/cola/primero", response_model=RespuestaVuelo,
         summary="Obtener primer vuelo",
         description="Retorna el primer vuelo de la lista (próximo a salir).")
def obtener_primer_vuelo(gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    vuelo = gestor.obtener_primer_vuelo()
    if vuelo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay vuelos en la cola")
    return vuelo

@app.get("/vuelos/cola/ultimo", response_model=RespuestaVuelo,
         summary="Obtener último vuelo",
         description="Retorna el último vuelo de la lista.")
def obtener_ultimo_vuelo(gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    vuelo = gestor.obtener_ultimo_vuelo()
    if vuelo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay vuelos en la cola")
    return vuelo
@app.get("/vuelos/filtrar/estado/{estado}", response_model=List[RespuestaVuelo],
         summary="Filtrar vuelos por estado",
         description="Retorna todos los vuelos que tienen un estado específico.")
def filtrar_vuelos_por_estado(
    estado: str, 
    gestor: GestorVuelos = Depends(obtener_gestor_vuelos)
):
    estados_validos = ["programado", "abordando", "despegado", "retrasado", "cancelado"]
    if estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
        )
    
    vuelos = gestor.obtener_vuelos_por_estado(estado)
    return vuelos

@app.get("/vuelos/filtrar/aerolinea/{aerolinea}", response_model=List[RespuestaVuelo],
         summary="Filtrar vuelos por aerolínea",
         description="Retorna todos los vuelos de una aerolínea específica.")
def filtrar_vuelos_por_aerolinea(
    aerolinea: str,
    gestor: GestorVuelos = Depends(obtener_gestor_vuelos)
):
    vuelos = gestor.obtener_vuelos_por_aerolinea(aerolinea)
    return vuelos

@app.get("/vuelos/filtrar/ruta", response_model=List[RespuestaVuelo],
         summary="Filtrar vuelos por origen/destino",
         description="Retorna todos los vuelos que coinciden con el origen y/o destino especificados.")
def filtrar_vuelos_por_ruta(
    origen: Optional[str] = None,
    destino: Optional[str] = None,
    gestor: GestorVuelos = Depends(obtener_gestor_vuelos)
):
    if origen is None and destino is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos origen o destino"
        )
        
    vuelos = gestor.obtener_vuelos_por_origen_destino(origen, destino)
    return vuelos

@app.post("/vuelos/reordenar/retrasos", response_model=List[RespuestaVuelo],
          summary="Reordenar vuelos por retrasos",
          description="Reordena los vuelos colocando los retrasados al final de la lista.")
def reordenar_vuelos_por_retrasos(gestor: GestorVuelos = Depends(obtener_gestor_vuelos)):
    return gestor.reordenar_vuelos_por_retrasos()

@app.get("/vuelos/buscar/{numero_vuelo}", response_model=RespuestaVuelo,
         summary="Buscar vuelo por número",
         description="Busca un vuelo específico por su número de vuelo.")
def buscar_vuelo_por_numero(
    numero_vuelo: str,
    gestor: GestorVuelos = Depends(obtener_gestor_vuelos)
):
    vuelo = gestor.buscar_vuelo_por_numero(numero_vuelo)
    if vuelo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return vuelo