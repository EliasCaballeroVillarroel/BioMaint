from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from crud.errores import (
    ConflictoError,
    DatosInvalidosError,
    NoEncontradoError,
)
from routers.equipos import router as equipos_router
from routers.clinicas import router as clinicas_router
from routers.ubicaciones import router as ubicaciones_router
from routers.fallas import router as fallas_router
from routers.mantenimientos import router as mantenimientos_router
from routers.tecnicos import router as tecnicos_router
from routers.contratos import router as contratos_router

app = FastAPI(
    title="BioMaint API",
    description="API para gestionar equipos médicos y su mantenimiento.",
    version="0.1.0"
)

app.include_router(equipos_router)
app.include_router(clinicas_router)
app.include_router(ubicaciones_router)
app.include_router(fallas_router)
app.include_router(mantenimientos_router)
app.include_router(tecnicos_router)
app.include_router(contratos_router)

# Errores de negocio lanzados por el CRUD (crud/errores.py) -> HTTP.
CODIGOS_POR_ERROR = {
    NoEncontradoError: 404,
    ConflictoError: 409,
    DatosInvalidosError: 422,
}


def manejar_error_negocio(request: Request, exc: Exception):
    # isinstance y no type(): incluye subclases como NumeroSerieDuplicadoError.
    codigo = next(
        codigo
        for clase, codigo in CODIGOS_POR_ERROR.items()
        if isinstance(exc, clase)
    )
    return JSONResponse(status_code=codigo, content={"detail": str(exc)})


for clase_error in CODIGOS_POR_ERROR:
    app.add_exception_handler(clase_error, manejar_error_negocio)


@app.exception_handler(IntegrityError)
async def manejar_error_integridad(
    request: Request,
    exc: IntegrityError
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "La operación no se pudo completar porque "
                "viola una restricción de integridad de la base de datos."
            )
        }
    )


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a BioMaint API",
        "estado": "funcionando"
    }


@app.get("/salud")
def verificar_estado():
    return {
        "api": "activa",
        "base_de_datos": "sin verificar"
    }
