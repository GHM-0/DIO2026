CREATE DATABASE IF NOT EXISTS DIOBANK;
USE DIOBANK;

/* Deve Conter USUÁRIOS e PRIVILÉGIOS */
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'app_user_pass';

-- Restrição do perfil da app

GRANT SELECT, INSERT, UPDATE, DELETE ON DIOBANK.* TO 'app_user'@'%';

-- Aplicação dos privilégios
FLUSH PRIVILEGES;