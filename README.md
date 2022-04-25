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
- 'grant all on interessant.* to 'interessantapp'@'localhost';'

finally, run api.py.
if you see a message like 'Unable to bind to port', either run as root or change the port. 
