#db.py: some database utilities
import logging
import os
import inspect

import pymysql

class db:
    def __init__(self, password, ip, database):
        self.databasepassword = password
        if not ip:
            ip = "localhost"
        self.ip = ip
        self.database = database
        self.logger = logging.getLogger(name=f'db')
        self.conn = self.attempt_connection()
        self.logger.info("Connected to database.")

    def requires_connection(func):
        def requires_connection_inner(self, *args, **kwargs):
            """Attempts a reconnect if OperationalError is raised"""
            try:
                self.logger.info(f"Calling {func.__name__} with {args}")
                return func(self, *args, **kwargs)
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                self.logger.info("db connection lost, reconnecting")
                self.reconnect()
                return func(self, *args, **kwargs)
        return requires_connection_inner

    def attempt_connection(self):
        self.logger.info(f"Attempting to connect to database '{self.database}' on '{self.ip}'...")
        return self.connect()

    def reconnect(self):
        self.conn = self.connect()

    def connect(self):
        conn = pymysql.connect(host=self.ip,
                    user="interessantapp",
                    password=self.databasepassword,
                    db=self.database,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True).cursor()
        return conn

    @requires_connection
    def exec_safe_query(self, query, params, *, debug=False, fetchall=False):
        """Executes 'query' with 'params'. Uses pymysql's parameterized queries.

        Parameters
        ----------
        query : str
            The SQL query to execute. 
        password : str, optional
            The database password in plain text. TODO: why is this optional
        ip : str, optional
            The IP address to use for the database. Defaults to 'localhost'. Optional if `bot` has a `dbip` attribute.
        database : str, optional
            The name of the database to connect to. Optional if `bot` has a `database` attribute. 
        """
        self.conn.execute(str(query), params)
        row = self.conn.fetchall()
        if len(row) == 1:
            row = row[0]
        return row if row != () and row != "()" else None
