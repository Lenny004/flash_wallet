CREATE DATABASE IF NOT EXISTS dbflash;
USE dbflash;

CREATE TABLE tbusuario(
    id_usuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contra VARCHAR(500) NOT NULL,
    img_usuario VARCHAR(100) NULL
);

CREATE TABLE tbtarjeta_digital(
	id_tarjeta INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    pan VARCHAR(19) NOT NULL UNIQUE,
    cvc TINYINT UNSIGNED,
    balance DECIMAL(7,2) NOT NULL,
    fecha_creacion DATE NOT NULL,
    fecha_actualizacion DATETIME NOT NULL,
    id_usuario INT NOT NULL UNIQUE
);

CREATE TABLE tbhistorial(
	id_historial INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    monto_agregado DECIMAL(7,2) NOT NULL,
    fecha_historial DATE NOT NULL,
    hora_historial TIME NOT NULL,
    id_tarjeta INT NOT NULL
);

alter table tbtarjeta_digital
add constraint fk_usuario
foreign key (id_usuario)
references tbusuario(id_usuario);

alter table tbhistorial
add constraint fk_tarjeta
foreign key (id_tarjeta)
references tbtarjeta_digital(id_tarjeta);

CREATE TABLE tbservicios(
	id_servicio INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    img_servicio VARCHAR(100) NOT NULL
);

CREATE TABLE tbestado(
    id_estado INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    estado VARCHAR(10) NOT NULL
);

CREATE TABLE tbtransaccion(
	id_transaccion INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha_transaccion DATE NOT NULL,
    hora_transaccion TIME NOT NULL,
    monto DECIMAL(7,2) NOT NULL,
    frecuencia INT NOT NULL,
    descripcion VARCHAR(40) NOT NULL,
    id_tarjeta INT NOT NULL,
    id_servicio INT NOT NULL,
    id_estado INT NOT NULL
);

alter table tbtransaccion
add constraint fk_tarjeta2
foreign key (id_tarjeta)
references tbtarjeta_digital(id_tarjeta);

alter table tbtransaccion
add constraint fk_servicio
foreign key (id_servicio)
references tbservicios(id_servicio);

alter table tbtransaccion
add constraint fk_estado
foreign key (id_estado)
references tbestado(id_estado);

CREATE TABLE tbfactura(
	id_factura INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha_factura DATE NOT NULL,
    hora_factura TIME NOT NULL,
    monto_total DECIMAL(6,2) NOT NULL,
    id_transaccion INT NOT NULL
);

alter table tbfactura
add constraint fk_transaccion
foreign key (id_transaccion)
references tbtransaccion(id_transaccion);

INSERT INTO tbestado(estado)VALUES
('Pendiente'),
('En espera'),
('Completada');

INSERT INTO tbservicios(nombre, img_servicio)VALUES
('Claro', 'Claro.png'),
('Tigo', 'Tigo.png'),
('Movistar', 'Movistar.png'),
('Tropigas', 'Tropigas.png'),
('ANDA', 'Anda.png'),
('AES', 'Aes.png'),
('DELSUR', 'Delsur.png');