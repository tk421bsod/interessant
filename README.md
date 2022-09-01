# interessant

a link shortener with a minimalist design.

### hosting

first, install:
- python3.8+
- mariadb (mysql is fine as well)
- python3-pip (if using Linux)
- aiohttp (through pip)
- pymysql (also through pip)

the `aiohttp-compress` Python module is optional, but highly recommended as it adds support for gzip compression.
this can reduce file sizes by as much as 84% (bootstrap.min.css benefits the most from this) at the cost of increased cpu usage.

next, set up the database:
- enter mysql shell (might need to run this as root)
- 'create database interessant;'
- 'create user 'interessantapp'@'localhost';'
- 'use interessant;'
- 'create table links(url text, hash varchar(11) primary key);'
- 'grant all on interessant.* to 'interessantapp'@'localhost';'
- 'flush privileges;'

finally, run api.py.
if you see an error message like 'Unable to bind to port', either run as root or change the port. (located in web.run_app() on the last line of api.py) 
