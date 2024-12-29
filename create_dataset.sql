CREATE DATABASE pico;

USE pico;

CREATE TABLE mqtt (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    temperature	FLOAT,
    pressure	FLOAT,
    humidity	FLOAT,
    CO2 FLOAT,
    TVOC	FLOAT,
    Date TIMESTAMP DEFAULT NOW()
);