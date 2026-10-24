/*INSERT INTO clinicas (nombre, direccion)
VALUES
    ('Clinica Allende', 'Av. Hipólito Yrigoyen 384'),
    ('Hospital Córdoba', 'Av. Patria 656');

INSERT INTO ubicaciones (clinica_id, servicio, sector, piso, sala)
VALUES
    (1, 'Diagnostico por Imagenes', 'Resonancia', '1', 'Sala 101'),
    (1, 'Diagnostico por Imagenes', 'Tomografia', '1', 'Sala 102'),
    (1, 'Hemodinamia', 'Cardiologia', '2', 'Sala 201'),
    (2, 'Diagnostico por Imagenes', 'Radiologia', '1', 'Sala 105'),
    (2, 'Cirugia', 'Quirofano', '2', 'Quirofano 3');
    
SELECT * FROM clinicas;
SELECT * FROM ubicaciones;

-- EQUIPOS 
-- Resonancia Allende
INSERT INTO equipos
(ubicacion_id, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, estado_actual)
VALUES
(1, 'Resonador Magnetico', 'Resonancia Magnetica', 'MAGNETOM Aera', 'Siemens', 'SN-RES-001', '2021-03-15', '2021-05-10', 'ACTIVO'),
(1, 'Bobina de Cabeza', 'Bobina MRI', 'Head Coil 20ch', 'Siemens', 'SN-RES-002', '2021-03-15', '2021-05-10', 'ACTIVO'),
(1, 'Bobina de Rodilla', 'Bobina MRI', 'Knee 15ch', 'Siemens', 'SN-RES-003', '2021-03-15', '2021-05-10', 'ACTIVO'),
(1, 'Monitor de Paciente', 'Monitor Multiparametrico', 'Infinity Delta', 'Dräger', 'SN-RES-004', '2021-04-20', '2021-05-10', 'ACTIVO'),
(1, 'Inyector de Contraste', 'Inyector MRI', 'Spectris Solaris EP', 'Medrad', 'SN-RES-005', '2021-04-25', '2021-05-10', 'EN_MANTENIMIENTO');
-- Tomografía Allende
INSERT INTO equipos
(ubicacion_id, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, estado_actual)
VALUES
(2, 'Tomografo Computado', 'Tomografia', 'SOMATOM go.Top', 'Siemens', 'SN-TC-001', '2022-02-10', '2022-04-15', 'ACTIVO'),
(2, 'Inyector de Contraste', 'Inyector CT', 'Stellant', 'Medrad', 'SN-TC-002', '2022-02-15', '2022-04-15', 'ACTIVO'),
(2, 'Monitor de Paciente', 'Monitor Multiparametrico', 'B40', 'GE', 'SN-TC-003', '2022-03-01', '2022-04-15', 'ACTIVO'),
(2, 'Estacion de Trabajo', 'Workstation', 'Syngo CT', 'Siemens', 'SN-TC-004', '2022-03-05', '2022-04-15', 'ACTIVO'),
(2, 'UPS', 'Sistema UPS', 'Smart-UPS 3000', 'APC', 'SN-TC-005', '2022-03-10', '2022-04-15', 'ACTIVO');
-- Hemodinamia Allende
INSERT INTO equipos
(ubicacion_id, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, estado_actual)
VALUES
(3, 'Angiografo', 'Angiografia', 'Artis Zee', 'Siemens', 'SN-HEM-001', '2020-06-10', '2020-08-20', 'ACTIVO'),
(3, 'Inyector de Contraste', 'Inyector Angiografico', 'Mark 7 Arterion', 'Medrad', 'SN-HEM-002', '2020-06-15', '2020-08-20', 'ACTIVO'),
(3, 'Monitor Hemodinamico', 'Monitor Hemodinamia', 'Mac-Lab XT', 'GE', 'SN-HEM-003', '2020-07-01', '2020-08-20', 'ACTIVO'),
(3, 'Desfibrilador', 'Desfibrilador', 'LIFEPAK 20e', 'Physio-Control', 'SN-HEM-004', '2020-07-15', '2020-08-20', 'ACTIVO'),
(3, 'Electrocardiografo', 'ECG', 'MAC 2000', 'GE', 'SN-HEM-005', '2020-07-20', '2020-08-20', 'ACTIVO');
-- Radiología Hospital Córdoba 
INSERT INTO equipos
(ubicacion_id, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, estado_actual)
VALUES
(4, 'Equipo de Rayos X', 'Radiografia', 'Ysio Max', 'Siemens', 'SN-RAD-001', '2019-01-15', '2019-03-20', 'ACTIVO'),
(4, 'Equipo de Rayos X', 'Radiografia', 'Discovery XR656', 'GE', 'SN-RAD-002', '2020-05-10', '2020-07-15', 'ACTIVO'),
(4, 'Mamografo', 'Mamografia', 'Mammomat Revelation', 'Siemens', 'SN-RAD-003', '2021-08-01', '2021-10-10', 'ACTIVO'),
(4, 'Equipo de Rayos X Portatil', 'Radiografia Portatil', 'MobileDaRt Evolution', 'Shimadzu', 'SN-RAD-004', '2022-01-20', '2022-03-15', 'ACTIVO'),
(4, 'Digitalizador CR', 'Radiologia Computada', 'CR 10-X', 'Agfa', 'SN-RAD-005', '2019-02-10', '2019-03-20', 'INACTIVO');
-- Quirofano Hospital Cordoba 
INSERT INTO equipos
(ubicacion_id, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, estado_actual)
VALUES
(5, 'Mesa Quirurgica', 'Mesa Quirurgica', 'TruSystem 7500', 'Trumpf', 'SN-QX-001', '2021-04-10', '2021-06-15', 'ACTIVO'),
(5, 'Lampara Quirurgica', 'Lampara Quirurgica', 'Pendants 585', 'Dräger', 'SN-QX-002', '2021-04-15', '2021-06-15', 'ACTIVO'),
(5, 'Maquina de Anestesia', 'Anestesia', 'Flow-i', 'Maquet', 'SN-QX-003', '2021-05-01', '2021-06-15', 'ACTIVO'),
(5, 'Electrobisturi', 'Electrocirugia', 'Force FX-C', 'Valleylab', 'SN-QX-004', '2021-05-10', '2021-06-15', 'ACTIVO'),
(5, 'Monitor Multiparametrico', 'Monitor Multiparametrico', 'B40', 'GE', 'SN-QX-005', '2021-05-15', '2021-06-15', 'EN_MANTENIMIENTO');
SELECT * FROM equipos; -- Seleccionar todos los equipos 
SELECT COUNT(*) AS cantidad_equipos
FROM equipos; -- Cuantos equipos tenemos 
SELECT marca, COUNT(*) AS cantidad
FROM equipos
GROUP BY marca
ORDER BY cantidad DESC; -- Que marcas tenemos 

-- Cargamos TECNICOS 
INSERT INTO tecnicos (nombre, apellido, empresa)
VALUES
    ('Carlos', 'Gomez', 'Siemens'),
    ('Martin', 'Rodriguez', 'Siemens'),
    ('Luciano', 'Fernandez', 'GE HealthCare'),
    ('Andres', 'Martinez', 'GE HealthCare'),
    ('Pablo', 'Sanchez', 'Medrad'),
    ('Nicolas', 'Romero', 'Philips'),
    ('Federico', 'Torres', 'Drager'),
    ('Matias', 'Diaz', 'Medtronic'),
    ('Santiago', 'Alvarez', 'Servicio Tecnico Independiente'),
    ('Javier', 'Moreno', 'Servicio Tecnico Independiente');

-- Cargamos FALLAS  

INSERT INTO fallas
(equipo_id, tipo_falla, descripcion_falla, fecha_falla, fecha_resolucion, severidad)
VALUES
(1, 'Refrigeracion', 'Temperatura del sistema de refrigeracion fuera de rango.', '2024-02-15', '2024-02-17', 'ALTA'),

(1, 'Bobina', 'Intermitencia en bobina durante adquisicion de imagen.', '2024-09-08', '2024-09-10', 'MEDIA'),

(2, 'Conexion', 'Perdida intermitente de comunicacion con la bobina.', '2025-01-20', '2025-01-21', 'MEDIA'),

(3, 'Bobina', 'Artefactos en imagen durante estudios de rodilla.', '2025-04-12', '2025-04-15', 'MEDIA'),

(4, 'Pantalla', 'Pantalla del monitor presenta apagados intermitentes.', '2024-06-05', '2024-06-06', 'BAJA'),

(5, 'Inyector', 'Falla en el mecanismo de inyeccion de contraste.', '2025-02-10', '2025-02-13', 'ALTA'),

(6, 'Gantry', 'Ruido anormal durante la rotacion del gantry.', '2024-03-18', '2024-03-22', 'ALTA'),

(6, 'Detector', 'Disminucion de calidad de imagen por detector.', '2025-07-02', '2025-07-06', 'ALTA'),

(7, 'Bomba', 'Presion de inyeccion inferior al valor configurado.', '2024-11-11', '2024-11-13', 'MEDIA'),

(8, 'Alimentacion', 'Reinicio inesperado del monitor durante estudios.', '2025-03-05', '2025-03-06', 'MEDIA'),

(9, 'Software', 'Error de aplicacion durante procesamiento de imagenes.', '2024-08-21', '2024-08-22', 'BAJA'),

(10, 'Bateria', 'Autonomia reducida de la UPS.', '2025-05-17', '2025-05-19', 'MEDIA'),

(11, 'Movimiento', 'Limitacion intermitente del movimiento de la mesa.', '2024-04-10', '2024-04-15', 'ALTA'),

(11, 'Imagen', 'Artefactos visibles durante adquisicion angiografica.', '2025-08-14', NULL, 'ALTA'),

(13, 'Comunicacion', 'Perdida de comunicacion con modulo de adquisicion.', '2024-10-03', '2024-10-05', 'MEDIA'),

(14, 'Bateria', 'Bateria no mantiene carga nominal.', '2025-01-08', '2025-01-10', 'ALTA'),

(16, 'Generador', 'Error intermitente del generador de rayos X.', '2024-07-19', '2024-07-23', 'ALTA'),

(18, 'Compresion', 'Compresion no alcanza la fuerza configurada.', '2025-06-11', '2025-06-14', 'MEDIA'),

(20, 'Digitalizacion', 'Lineas y artefactos durante digitalizacion de placas.', '2024-12-02', '2024-12-04', 'MEDIA'),

(25, 'SpO2', 'Lecturas intermitentes del modulo de oximetria.', '2025-09-15', NULL, 'MEDIA');

-- Fallas no resueltas 
SELECT *
FROM fallas
WHERE fecha_resolucion IS NULL; 
-- Cuantas fallas tuvo cada equipo 
SELECT equipo_id, COUNT(*) AS cantidad_fallas
FROM fallas
GROUP BY equipo_id
ORDER BY cantidad_fallas DESC;
-- Cuantas fallas de cada severidad tenemos 
SELECT severidad, COUNT(*) AS cantidad
FROM fallas
GROUP BY severidad;

INSERT INTO mantenimientos
(equipo_id, falla_id, fecha, tipo_mantenimiento, duracion_mantenimiento, descripcion, resultado)
VALUES

-- RESONADOR
(1, NULL, '2024-01-15', 'PREVENTIVO', 180,
 'Inspeccion general del resonador y verificacion del sistema de refrigeracion.',
 'Equipo operativo.'),

(1, 1, '2024-02-17', 'CORRECTIVO', 360,
 'Reparacion del sistema de refrigeracion luego de detectar temperatura fuera de rango.',
 'Falla resuelta.'),

(1, NULL, '2024-07-20', 'PREVENTIVO', 150,
 'Mantenimiento preventivo general y verificacion de bobinas.',
 'Equipo operativo.'),

(1, 2, '2024-09-10', 'CORRECTIVO', 240,
 'Diagnostico y reparacion de intermitencia en bobina.',
 'Falla resuelta.'),

-- BOBINA CABEZA
(2, 3, '2025-01-21', 'CORRECTIVO', 120,
 'Revision de conexion y comunicacion de bobina.',
 'Falla resuelta.'),

(2, NULL, '2025-06-10', 'PREVENTIVO', 90,
 'Inspeccion de conectores y limpieza.',
 'Equipo operativo.'),

-- BOBINA RODILLA
(3, 4, '2025-04-15', 'CORRECTIVO', 180,
 'Revision y ajuste de bobina por presencia de artefactos.',
 'Falla resuelta.'),

-- MONITOR RESONANCIA
(4, 5, '2024-06-06', 'CORRECTIVO', 120,
 'Revision de alimentacion y reemplazo de componente defectuoso.',
 'Falla resuelta.'),

(4, NULL, '2025-02-05', 'PREVENTIVO', 60,
 'Limpieza y verificacion funcional del monitor.',
 'Equipo operativo.'),

-- INYECTOR MRI
(5, 6, '2025-02-13', 'CORRECTIVO', 240,
 'Reparacion del mecanismo de inyeccion.',
 'Falla resuelta.'),

(5, NULL, '2025-08-10', 'PREVENTIVO', 120,
 'Calibracion y prueba funcional del inyector.',
 'Equipo operativo.'),

-- TOMOGRAFO
(6, NULL, '2024-01-20', 'PREVENTIVO', 240,
 'Mantenimiento preventivo del tomografo y verificacion mecanica.',
 'Equipo operativo.'),

(6, 7, '2024-03-22', 'CORRECTIVO', 480,
 'Inspeccion y reparacion del sistema de rotacion del gantry.',
 'Falla resuelta.'),

(6, NULL, '2024-09-15', 'PREDICTIVO', 180,
 'Analisis de vibraciones y comportamiento mecanico del gantry.',
 'Sin anomalías críticas.'),

(6, 8, '2025-07-06', 'CORRECTIVO', 420,
 'Diagnostico y reemplazo del componente asociado al detector.',
 'Falla resuelta.'),

-- INYECTOR CT
(7, 9, '2024-11-13', 'CORRECTIVO', 180,
 'Revision del sistema de presion de inyeccion.',
 'Falla resuelta.'),

(7, NULL, '2025-05-12', 'PREVENTIVO', 90,
 'Calibracion del sistema de inyeccion.',
 'Equipo operativo.'),

-- MONITOR CT
(8, 10, '2025-03-06', 'CORRECTIVO', 120,
 'Revision del sistema de alimentacion del monitor.',
 'Falla resuelta.'),

-- WORKSTATION
(9, 11, '2024-08-22', 'CORRECTIVO', 150,
 'Reinstalacion y correccion de software de procesamiento.',
 'Falla resuelta.'),

(9, NULL, '2025-04-20', 'PREVENTIVO', 120,
 'Mantenimiento del sistema operativo y aplicaciones.',
 'Equipo operativo.'),

-- UPS
(10, 12, '2025-05-19', 'CORRECTIVO', 180,
 'Reemplazo de bateria de UPS.',
 'Falla resuelta.'),

(10, NULL, '2025-11-10', 'PREDICTIVO', 60,
 'Evaluacion del estado de bateria mediante pruebas de autonomia.',
 'Bateria dentro de parametros.'),

-- ANGIOGRAFO
(11, NULL, '2024-01-25', 'PREVENTIVO', 240,
 'Inspeccion general del angiografo y sistema de movimiento.',
 'Equipo operativo.'),

(11, 13, '2024-04-15', 'CORRECTIVO', 360,
 'Revision del sistema de movimiento de mesa.',
 'Falla resuelta.'),

(11, 14, '2025-08-20', 'CORRECTIVO', 300,
 'Diagnostico de artefactos y revision del sistema de adquisicion.',
 'Falla pendiente de resolucion.'),

-- MONITOR HEMODINAMIA
(13, 15, '2024-10-05', 'CORRECTIVO', 120,
 'Revision de comunicacion con modulo de adquisicion.',
 'Falla resuelta.'),

(13, NULL, '2025-05-20', 'PREVENTIVO', 90,
 'Limpieza y verificacion de funcionamiento.',
 'Equipo operativo.'),

-- DESFIBRILADOR
(14, 16, '2025-01-10', 'CORRECTIVO', 180,
 'Reemplazo de bateria y pruebas de descarga.',
 'Falla resuelta.'),

-- RAYOS X
(16, 17, '2024-07-23', 'CORRECTIVO', 300,
 'Diagnostico y reparacion del generador.',
 'Falla resuelta.'),

-- MAMOGRAFO
(18, 18, '2025-06-14', 'CORRECTIVO', 240,
 'Ajuste y calibracion del sistema de compresion.',
 'Falla resuelta.'),

-- DIGITALIZADOR
(20, 19, '2024-12-04', 'CORRECTIVO', 180,
 'Limpieza y calibracion del sistema de digitalizacion.',
 'Falla resuelta.'),

-- MONITOR QUIROFANO
(25, NULL, '2025-03-15', 'PREVENTIVO', 90,
 'Inspeccion general del monitor y modulos de paciente.',
 'Equipo operativo.'),

(25, 20, '2025-09-16', 'CORRECTIVO', 120,
 'Revision del modulo de oximetria.',
 'Falla pendiente de resolucion.');
 
 -- Si el mantenimiento tiene un numero de falla id es pq nacio por esa falla 
 -- Si el mantenimiento tiene un numero NULL es pq no nacio por una falla, es preventivo 
 -- Cuantos mantnimientos hay 
 SELECT COUNT(*) AS cantidad_mantenimientos
FROM mantenimientos;
-- Cuantos de cada tipo 
SELECT tipo_mantenimiento, COUNT(*) AS cantidad
FROM mantenimientos
GROUP BY tipo_mantenimiento;
-- Cuanto es el tiempo promedio 
SELECT AVG(duracion_mantenimiento) AS promedio_minutos
FROM mantenimientos;
-- Cuantos mantenimientos tuvo cada equipo 
SELECT equipo_id, COUNT(*) AS cantidad_mantenimientos
FROM mantenimientos
GROUP BY equipo_id
ORDER BY cantidad_mantenimientos DESC;

-- Cargamos quien hizo los mantenimientos 

INSERT INTO mantenimiento_tecnicos (mantenimiento_id, tecnico_id)
VALUES
-- Resonador
(1, 1),
(2, 1),
(2, 2),
(3, 2),
(4, 1),
(4, 2),

-- Bobinas
(5, 1),
(6, 2),
(7, 1),

-- Monitor e inyector MRI
(8, 7),
(9, 7),
(10, 5),
(11, 5),

-- Tomografo
(12, 1),
(13, 1),
(13, 3),
(14, 1),
(15, 1),
(15, 3),

-- Inyector CT / monitor / workstation
(16, 5),
(17, 5),
(18, 3),
(19, 3),
(20, 3),

-- UPS
(21, 9),
(22, 9),

-- Angiografo
(23, 1),
(24, 1),
(24, 2),
(25, 1),
(25, 2),

-- Monitor hemodinamia
(26, 3),
(27, 3),

-- Desfibrilador
(28, 8),

-- Rayos X
(29, 3),
(30, 3),
(30, 4),

-- Mamografo
(31, 1),
(31, 2),

-- Digitalizador
(32, 6),

-- Monitor quirofano
(33, 7),
(33, 8);
*/

-- Hacemos un JOIN 

SELECT
    m.id AS mantenimiento,
    e.nombre AS equipo,
    e.marca,
    m.fecha,
    m.tipo_mantenimiento,
    CONCAT(t.nombre, ' ', t.apellido) AS tecnico,
    t.empresa
FROM mantenimientos m
JOIN equipos e
    ON m.equipo_id = e.id
JOIN mantenimiento_tecnicos mt
    ON m.id = mt.mantenimiento_id
JOIN tecnicos t
    ON mt.tecnico_id = t.id
ORDER BY m.id;