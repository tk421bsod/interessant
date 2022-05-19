# interessant

a link shortener with a minimalist design.

### hosting

first, install:
- python3.8+
- mysql
- python3-pip (if using Linux)
- aiohttp (through pip)
- pymysql (also through pip)

next, set up the database:
- enter mysql shell (probably will need to run as root)
- 'create database interessant;'
- 'create user 'interessantapp'@'localhost';'
- 'create table links(url text, hash varchar(11) primary key);'
- 'grant all on interessant.* to 'interessantapp'@'localhost';'
- 'flush privileges;'

finally, run api.py.
if you see an error message like 'Unable to bind to port', either run as root or change the port. 
