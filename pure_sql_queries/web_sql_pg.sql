CREATE TABLE web_user (
    inc SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    description VARCHAR(200)
);

CREATE TABLE web_resource_type (
    inc SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE web_resource (
    inc SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    type INT NOT NULL
        REFERENCES web_resource_type (inc)
        ON DELETE CASCADE
);

CREATE TABLE web_access (
	id SERIAL PRIMARY KEY,
    user_inc INT NOT NULL
        REFERENCES web_user (inc)
        ON DELETE CASCADE,
    web_resource_inc INT NOT NULL
        REFERENCES web_resource (inc)
        ON DELETE CASCADE,
    has_access BOOLEAN NOT NULL DEFAULT TRUE
);