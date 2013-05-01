-- The photos table (for testing purposes will later be removed)
DROP TABLE IF EXISTS photos;
CREATE TABLE photos (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       filename TEXT NOT NULL
);

DROP TABLE IF EXISTS tempusers;
CREATE TABLE tempusers (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       verifyId VARCHAR(64) NOT NULL UNIQUE,
       username VARCHAR(32) NOT NULL UNIQUE,
       password VARCHAR(60) NOT NULL, -- bcrypt password storage
       email	TEXT	    NOT NULL,
       created  DATETIME    NOT NULL
 );
 
-- The users table
DROP TABLE IF EXISTS users;
CREATE TABLE users (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
       username VARCHAR(32) NOT NULL UNIQUE,
       password VARCHAR(60) NOT NULL, -- bcrypt password storage
       email	TEXT	    NOT NULL
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
       id VARCHAR(64) PRIMARY KEY,
       uId INT,
       lastactive DATETIME NOT NULL
);

DROP TABLE IF EXISTS decks;
CREATE TABLE decks (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(256) NOT NULL,
       deck_id VARCHAR(16) UNIQUE,
       creator INT NOT NULL,
       description TEXT,
       hash VARCHAR(32) NOT NULL
);

DROP TABLE IF EXISTS cards;
CREATE TABLE cards (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       deck INT NOT NULL,
       sidea TEXT,
       sideb TEXT,
       card_id INT,
       hash VARCHAR(32) NOT NULL
);

DROP TABLE IF EXISTS resources;
CREATE TABLE resources (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       cId INT NOT NULL,
       resource_id VARCHAR(8) UNIQUE NOT NULL,
       name TEXT,
       path TEXT,
       hash VARCHAR(32) NOT NULL
);
