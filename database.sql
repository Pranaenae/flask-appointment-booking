CREATE TABLE accounts(
  id SERIAL PRIMARY KEY , 
  username varchar(255),
  password varchar(255)
);

INSERT INTO accounts (username, password) 
VALUES('pranay', 'pranay@123');
