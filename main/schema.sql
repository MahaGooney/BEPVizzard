DROP TABLE IF EXISTS 'BEP';
DROP TABLE IF EXISTS 'user';
DROP TABLE IF EXISTS 'role';

CREATE TABLE 'BEP' (
    'id' INT NOT NULL AUTOINCREMENT,
    'fixkosten'
    'varkosten'
    'verkaufspreis'
)

CREATE TABLE 'role' (
    'name' TEXT PRIMARY KEY,
    'permissions' INT NOT NULL,
    'standard' int
);

CREATE TABLE 'user' (
    'id' INT PRIMARY KEY AUTOINCREMENT,
    'username' TEXT NOT NULL,
    'email' TEXT NOT NULL,
    'password' TEXT NOT NULL,
    'role_id' TEXT NOT NULL,
    FOREIGN KEY ('role_id' REFERENCES 'role' (name)
);