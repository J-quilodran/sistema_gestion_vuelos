import re
from datetime import datetime, timedelta

class ValidadorVuelos:
    """Clase para validar los datos de vuelos antes de procesarlos"""
    
    @staticmethod
    def validar_numero_vuelo(numero_vuelo):
        """Valida el formato del número de vuelo (2 letras seguidas de 3-4 números)"""
        if not isinstance(numero_vuelo, str):
            return False, "El número de vuelo debe ser una cadena de texto"
            
        patron = r'^[A-Z]{2}\d{3,4}$'
        if not re.match(patron, numero_vuelo):
            return False, "Formato de número de vuelo inválido. Debe ser 2 letras mayúsculas seguidas de 3-4 números (ej: IB1234)"
            
        return True, "Número de vuelo válido"
    
    @staticmethod
    def validar_estado(estado):
        """Valida que el estado del vuelo sea uno permitido"""
        estados_validos = ["programado", "abordando", "despegado", "retrasado", "cancelado"]
        
        if estado not in estados_validos:
            return False, f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
            
        return True, "Estado válido"
    
    @staticmethod
    def validar_hora_programada(hora):
        """Valida que la hora programada sea una fecha futura (o actual)"""
        if not isinstance(hora, datetime):
            return False, "La hora programada debe ser un objeto datetime"
            
        # Verificar que la hora no sea en el pasado (más de 30 minutos)
        tiempo_minimo = datetime.now() - timedelta(minutes=30)
        if hora < tiempo_minimo:
            return False, "La hora programada no puede ser en el pasado"
            
        return True, "Hora programada válida"
    
    @staticmethod
    def validar_origen_destino(origen, destino):
        """Valida que origen y destino sean diferentes y formatos válidos"""
        if origen == destino:
            return False, "El origen y destino no pueden ser iguales"
            
        # Validar formato: códigos de aeropuerto (3 letras mayúsculas)
        patron = r'^[A-Z]{3}$'
        if not re.match(patron, origen):
            return False, "Código de origen inválido. Debe ser 3 letras mayúsculas (ej: MAD)"
            
        if not re.match(patron, destino):
            return False, "Código de destino inválido. Debe ser 3 letras mayúsculas (ej: BCN)"
            
        return True, "Origen y destino válidos"
    
    @staticmethod
    def validar_vuelo_completo(datos_vuelo):
        """Realiza todas las validaciones en los datos del vuelo"""
        errores = []
        
        # Validar número de vuelo
        valido, mensaje = ValidadorVuelos.validar_numero_vuelo(datos_vuelo.get('numero_vuelo', ''))
        if not valido:
            errores.append(mensaje)
            
        # Validar estado
        valido, mensaje = ValidadorVuelos.validar_estado(datos_vuelo.get('estado', ''))
        if not valido:
            errores.append(mensaje)
            
        # Validar hora programada
        valido, mensaje = ValidadorVuelos.validar_hora_programada(datos_vuelo.get('hora_programada'))
        if not valido:
            errores.append(mensaje)
            
        # Validar origen y destino
        valido, mensaje = ValidadorVuelos.validar_origen_destino(
            datos_vuelo.get('origen', ''), 
            datos_vuelo.get('destino', '')
        )
        if not valido:
            errores.append(mensaje)
            
        # Devolver resultado
        if errores:
            return False, errores
        return True, ["Todos los datos del vuelo son válidos"]
