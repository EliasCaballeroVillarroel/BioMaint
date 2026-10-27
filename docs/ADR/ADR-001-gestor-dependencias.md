# ADR-001: Gestor de dependencias

Fecha: 2026-10-27 · Estado: Aceptada

## Contexto
BioMant usaba pip con un requirements.txt generado por pip freeze: 32 paquetes
mezclando dependencias directas y transitivas, sin separar producción de desarrollo
y sin registrar la versión de Python. Al quitar un paquete, sus transitivas quedaban
huérfanas y eran indistinguibles de las directas. Se busca que el proyecto se pueda
reproducir por completo, fácil y rápido en cualquier computadora.

## Opciones
1. pip + pip-tools: viene con Python y ya se usaba. No elimina huérfanos, necesita
   herramientas extra para el lock y no gestiona la versión de Python.
2. uv: muy rápido, respeta el estándar pyproject.toml, genera lock (uv.lock),
   elimina huérfanos con uv sync y gestiona la versión de Python. Es joven y
   depende de una empresa (Astral).
3. Poetry: maduro y usado en empresas. Más lento y no instala Python.

## Decisión
Se elige uv. El riesgo de depender de una empresa se mitiga porque la configuración
sigue el estándar [project] de pyproject.toml: si uv deja de mantenerse, se puede
migrar a pip o Poetry sin reescribir nada, y uv.lock se puede exportar.

## Consecuencias
- Preparar el proyecto en otra computadora es un comando: uv sync.
- Los tests se corren con uv run pytest, sin activar el entorno.
- requirements.txt se mantiene solo como archivo generado (uv export), para quien
  no use uv. No se edita a mano.
- Se quitó el extra [standard] de uvicorn: pyyaml no tiene wheel para Python 3.15
  en Windows y el proyecto nunca lo usó.
- Al migrar subieron versiones (fastapi 0.143 → 0.162, entre otras); los 330 tests
  pasaron.
- pythonpath = ["."] en la config de pytest es temporal, hasta mover el código a un
  paquete app/ (T16).
- Riesgo: Python 3.15 es muy reciente; otros paquetes con partes en C podrían no
  tener wheel todavía.
- Revisar más adelante: README, CLAUDE.md, Dockerfile y CI deben usar uv.