-- Creazione del database "project"
CREATE DATABASE IF NOT EXISTS project;

-- Usa il database "project"
USE project;

-- Creazione della tabella 'employee'
CREATE TABLE IF NOT EXISTS employee (
  employee_id INT NOT NULL,
  name VARCHAR(20) NOT NULL,
  surname VARCHAR(20) NOT NULL,
  password VARCHAR(20) NOT NULL,
  PRIMARY KEY (employee_id)
);

-- Creazione della tabella 'room' (aggiungi le colonne necessarie)
CREATE TABLE IF NOT EXISTS room (
  room_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  -- Aggiungi altre colonne necessarie
  PRIMARY KEY (room_id)
);

-- Creazione della tabella 'reservations'
CREATE TABLE IF NOT EXISTS reservations (
  reservation_id INT NOT NULL AUTO_INCREMENT,
  employee_id INT NOT NULL,
  date DATE NOT NULL,
  starting_time TIME(0) NOT NULL,
  ending_time TIME(0) NOT NULL,
  room_id INT NOT NULL,
  PRIMARY KEY (reservation_id),
  FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
  FOREIGN KEY (room_id) REFERENCES room(room_id),
  CHECK(starting_time < ending_time)
);

-- Inserimento di un record nella tabella 'student'
INSERT INTO employee (employee_id, name, surname, password)
VALUES 
    ('198675', 'Giacomo', 'Zarba Meli', 'password1'),
    ('198676', 'Alessandro', 'Odri', 'password2'),
    ('198677', 'Riccardo', 'Mariotti', 'password3');

INSERT INTO room (room_id, name)
VALUES
    ('1', 'Frontend Developers'),
    ('2', 'Backend Developers'),
    ('3', 'Systems Engineers'),
    ('4', 'DevOps Engineers'),
    ('5', 'Sales');

-- Inserimento di un record nella tabella 'reservations'
-- Assicurati di avere un valore corretto per 'room_id' in base alla tua configurazione.
-- Sostituisci 'room_id' con l'ID corretto della classe a cui vuoi fare riferimento.
INSERT INTO reservations (employee_id, date, starting_time, ending_time, room_id)
VALUES 
    ('198675', '2022-11-23', '10:00:00', '11:00:00', '4');

