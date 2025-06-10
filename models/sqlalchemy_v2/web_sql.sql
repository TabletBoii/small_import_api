-- web_user
CREATE TABLE dbo.web_user (
    inc INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name VARCHAR(64)    NOT NULL UNIQUE,
    hashed_password VARCHAR(200) NOT NULL,
    description VARCHAR(200)     NULL
);
GO

-- web_resource_type
CREATE TABLE dbo.web_resource_type (
    inc INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name VARCHAR(64)    NOT NULL UNIQUE
);
GO

-- web_resource
CREATE TABLE dbo.web_resource (
    inc INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name VARCHAR(64)    NOT NULL UNIQUE,
    type INT            NOT NULL,
    CONSTRAINT FK_web_resource_type
        FOREIGN KEY(type) 
        REFERENCES dbo.web_resource_type(inc)
        ON DELETE CASCADE
);
GO

-- web_access
CREATE TABLE dbo.web_access (
    id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    user_inc           INT NOT NULL,
    web_resource_inc   INT NOT NULL,
    has_access         BIT NOT NULL CONSTRAINT DF_web_access_has_access DEFAULT(1),
    CONSTRAINT FK_web_access_user
        FOREIGN KEY(user_inc)
        REFERENCES dbo.web_user(inc)
        ON DELETE CASCADE,
    CONSTRAINT FK_web_access_resource
        FOREIGN KEY(web_resource_inc)
        REFERENCES dbo.web_resource(inc)
        ON DELETE CASCADE
);
GO