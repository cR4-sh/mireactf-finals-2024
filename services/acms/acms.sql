-- ALTER USER root with password 'root';

-- CREATE DATABASE acms;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c acms;

CREATE TABLE users (
    id          uuid        PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    CHAR(32)    UNIQUE NOT NULL,
    password    CHAR(32)    NOT NULL,
    group_id    uuid,
    access      INT         NOT NULL DEFAULT 0
    
);

CREATE TABLE groups (
    id          uuid        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        CHAR(32)    UNIQUE NOT NULL,
    head        uuid
);

CREATE TABLE devices (
    id          uuid        PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id    uuid        NOT NULL,
    device_type INT         NOT NULL, 
    access      INT         NOT NULL,
    access_key  CHAR(32)    NOT NULL
);

ALTER TABLE users ADD CONSTRAINT group_id FOREIGN KEY (group_id) REFERENCES groups(id);
ALTER TABLE users ADD CONSTRAINT access CHECK (access BETWEEN 0 AND 5);

ALTER TABLE groups ADD CONSTRAINT head FOREIGN KEY (head) REFERENCES users(id);

ALTER TABLE devices ADD CONSTRAINT group_id FOREIGN KEY (group_id) REFERENCES groups(id);
ALTER TABLE devices ADD CONSTRAINT access CHECK (access BETWEEN 0 AND 5);