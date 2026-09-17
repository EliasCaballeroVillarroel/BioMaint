class Equipo: 
    def __init__(self, nombre, equipo_id, serie, hospital, modelo):
        self.nombre = nombre 
        self.equipo_id = equipo_id
        self.serie = serie 
        self.hospital = hospital
        self.modelo = modelo 

    def mostrar_info(self) ->str: #->str indica que devuelve una str
        return f"El equipo es un {self.nombre} de id {self.equipo_id} modelo {self.modelo} ubicado en el hospital {self.hospital}"

