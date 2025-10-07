DROP DATABASE IF EXISTS veterinaria;
CREATE DATABASE veterinaria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE veterinaria;
-- Tabla rol
CREATE TABLE rol (
    idRol INT AUTO_INCREMENT PRIMARY KEY,
    nombreRol VARCHAR(100),
    descripcion TEXT,
    estado BOOLEAN
);

-- Tabla usuario
CREATE TABLE usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    correo VARCHAR(150) UNIQUE,
    contrasena VARCHAR(255),
    estado BOOLEAN,
    idRol INT,
    last_login DATETIME NULL,
    FOREIGN KEY (idRol) REFERENCES rol(idRol)
);

-- Tabla cliente
CREATE TABLE cliente (
    idCliente INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    correo VARCHAR(150)
);

-- Tabla mascota
CREATE TABLE mascota (
    idMascota INT AUTO_INCREMENT PRIMARY KEY,
    idCliente INT,
    nombreMascota VARCHAR(100),
    especie VARCHAR(50),
    raza VARCHAR(50),
    edad INT,
    sexo VARCHAR(10),
    FOREIGN KEY (idCliente) REFERENCES cliente(idCliente)
);

-- Tabla cita
CREATE TABLE cita (
    idCita INT AUTO_INCREMENT PRIMARY KEY,
    fechaCita DATE,
    horaCita TIME,
    estado VARCHAR(50),
    idCliente INT,
    idMascota INT,
    idUsuario INT,
    FOREIGN KEY (idCliente) REFERENCES cliente(idCliente),
    FOREIGN KEY (idMascota) REFERENCES mascota(idMascota),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
);

-- Tabla consulta
CREATE TABLE consulta (
    idConsulta INT AUTO_INCREMENT PRIMARY KEY,
    motivo TEXT,
    diagnostico TEXT,
    observaciones TEXT,
    costo DECIMAL(10,2),
    estado VARCHAR(50),
    idCita INT,
    idMascota INT,
    idUsuario INT,
    FOREIGN KEY (idCita) REFERENCES cita(idCita),
    FOREIGN KEY (idMascota) REFERENCES mascota(idMascota),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
);

-- Tabla historial médico
CREATE TABLE historialmedico (
    idHistorialMedico INT AUTO_INCREMENT PRIMARY KEY,
    idMascota INT,
    observacionesGenerales TEXT,
    fechaCreacion DATE,
    estado VARCHAR(50),
    idConsulta INT,
    FOREIGN KEY (idMascota) REFERENCES mascota(idMascota),
    FOREIGN KEY (idConsulta) REFERENCES consulta(idConsulta)
);

-- Tabla tratamiento
CREATE TABLE tratamiento (
    idTratamiento INT AUTO_INCREMENT PRIMARY KEY,
    nombreTratamiento VARCHAR(100),
    descripcion TEXT,
    duracion INT,
    costo DECIMAL(10,2),
    idConsulta INT,
    idMascota INT,
    FOREIGN KEY (idConsulta) REFERENCES consulta(idConsulta),
    FOREIGN KEY (idMascota) REFERENCES mascota(idMascota)
);

-- Tabla vacuna
CREATE TABLE vacuna (
    idVacuna INT AUTO_INCREMENT PRIMARY KEY,
    nombreVacuna VARCHAR(100),
    fechaAplicacion DATE,
    dosis VARCHAR(50),
    proximaDosis DATE,
    idMascota INT,
    FOREIGN KEY (idMascota) REFERENCES mascota(idMascota)
);

-- Tabla proveedor
CREATE TABLE proveedor (
    idProveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombreProveedor VARCHAR(100),
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    email VARCHAR(100)
);

-- Tabla producto
CREATE TABLE producto (
    idProducto INT AUTO_INCREMENT PRIMARY KEY,
    nombreProducto VARCHAR(100),
    stock INT,
    precioCompra DECIMAL(10,2),
    precioVenta DECIMAL(10,2)
);

-- Tabla compra
CREATE TABLE compra (
    idCompra INT AUTO_INCREMENT PRIMARY KEY,
    fechaCompra DATE,
    idProveedor INT,
    totalCompra DECIMAL(10,2),
    estado VARCHAR(50),
    FOREIGN KEY (idProveedor) REFERENCES proveedor(idProveedor)
);

-- Tabla detalle compra
CREATE TABLE detallecompra (
    idDetalleCompra INT AUTO_INCREMENT PRIMARY KEY,
    idCompra INT,
    idProducto INT,
    cantidad INT,
    precioUnitario DECIMAL(10,2),
    subTotal DECIMAL(10,2),
    FOREIGN KEY (idCompra) REFERENCES compra(idCompra),
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
);

-- Tabla movimiento inventario
CREATE TABLE movimientoinventario (
    idMovimientoInventario INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50),
    cantidad INT,
    fecha DATE,
    idProducto INT,
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
);

-- Tabla factura
CREATE TABLE factura (
    idFactura INT AUTO_INCREMENT PRIMARY KEY,
    fechaEmision DATE,
    idCliente INT,
    idConsulta INT,
    total DECIMAL(10,2),
    estadoPago VARCHAR(50),
    FOREIGN KEY (idCliente) REFERENCES cliente(idCliente),
    FOREIGN KEY (idConsulta) REFERENCES consulta(idConsulta)
);

-- Tabla detalle factura
CREATE TABLE detallefactura (
    idDetalleFactura INT AUTO_INCREMENT PRIMARY KEY,
    idFactura INT,
    idProducto INT,
    cantidad INT,
    precioUnitario DECIMAL(10,2),
    total DECIMAL(10,2),
    FOREIGN KEY (idFactura) REFERENCES factura(idFactura),
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
);

-- Tabla pago
CREATE TABLE pago (
    idPago INT AUTO_INCREMENT PRIMARY KEY,
    metodoPago VARCHAR(50),
    monto DECIMAL(10,2),
    fechaPago DATE,
    estadoPago VARCHAR(50),
    idFactura INT,
    FOREIGN KEY (idFactura) REFERENCES factura(idFactura)
);
-- ========================
-- DATOS INICIALES
-- ========================
INSERT INTO rol (nombreRol, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema', TRUE),
('Veterinario', 'Atiende consultas y tratamientos', TRUE),
('Recepcionista', 'Gestiona citas y facturación', TRUE);

-- Contraseña hasheada con Django (admin123)
INSERT INTO usuario (nombres, apellidos, correo, contrasena, estado, idRol, last_login)
VALUES ('Admin', 'Principal', 'admin@veterinaria.com',
'pbkdf2_sha256$1000000$RBdJy8R3QGaJ5yL9Hl91Br$NTGWYi3fqMM4j/VMXvdrXRIyKptpZe5H7ftojiV7YEE=',  
TRUE, 1, NULL);