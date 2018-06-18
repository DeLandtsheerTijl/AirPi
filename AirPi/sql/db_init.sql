CREATE USER 'airpi-admin'@'localhost' IDENTIFIED BY '!UuS4EkKH.';
CREATE USER 'airpi-web'@'localhost' IDENTIFIED BY '!CBy7rXGmB9.';
CREATE USER 'airpi-sensor'@'localhost' IDENTIFIED BY 'CBy7rXGmB9.';

CREATE DATABASE dbairpi;

GRANT ALL PRIVILEGES ON dbairpi.* to 'airpi-admin'@'localhost' WITH GRANT OPTION;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbairpi.* TO 'airpi-web'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON dbairpi.* TO 'airpi-sensor'@'localhost';
FLUSH PRIVILEGES;