DROP TABLE IF EXISTS 'BEP';
DROP TABLE IF EXISTS 'user';
DROP TABLE IF EXISTS 'role';

CREATE TABLE 'BEP' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'fixkosten' INT,
    'variable_kosten' INT,
    'preis' INT,
    'menge' INT
);

CREATE TABLE 'role' (
    'name' TEXT PRIMARY KEY,
    'permissions' INT NOT NULL,
    'standard' INT
);

CREATE TABLE 'user' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'name' TEXT NOT NULL,
    'email' TEXT NOT NULL,
    'password' TEXT NOT NULL,
    'role_id' TEXT NOT NULL,
    FOREIGN KEY ('role_id') REFERENCES 'role' (name)
);