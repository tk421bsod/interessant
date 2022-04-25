#db.py: some database utilities
import logging
import os
import inspect

import pymysql

class db:
    """
    Methods used for interaction with the database.

    This class provides no public attributes.

    Methods
    -------

    ensure_tables() - Ensures that all required tables exist.
    exec_safe_query(query, params, *,  fetchall) - Executes 'query' with 'params'. Uses pymysql's parameterized queries. 'params' can be empty.
    exec_query(query, *, fetchall) - Executes 'query'. DEPRECATED due to the potential for SQL injection. Will show a warning if used.
    """

    def __init__(self, password, ip, database):
        """
        Parameters
        ----------
        password : str, optional
            The database password in plain text.
        ip : str, optional
            The IP address to use for the database.
        database : str, optional
            The name of the database to connect to.
        """
        self.databasepassword = password
        if not ip:
            ip = "localhost"
        self.ip = ip
        self.database = database
        self.logger = logging.getLogger(name=f'db')
        #try to open a connection to the database
        self.conn = self.attempt_connection()
        self.logger.info("Connected to database.")

    def requires_connection(func):
        def requires_connection_inner(self, *args, **kwargs):
            """Reconnects to the database if the function raises an OperationalError"""
            try:
                self.logger.info(f"Calling {func.__name__} with {args}")
                return func(self, *args, **kwargs)
            except pymysql.err.OperationalError as e:
                if e.args[0] == 2013:
                    self.logger.info("db connection lost, reconnecting")
                    self.reconnect()
                    return func(self, *args, **kwargs)
                else:
                    raise
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

    #maybe make this an alias to exec_safe_query or rename exec_safe query to this?
    @requires_connection
    def exec_query(self, querytoexecute, debug=False, fetchall=False):
        self.connect(self.database)
        previous_frame = inspect.getframeinfo(inspect.currentframe().f_back)
        self.logger.error(f"db.exec_query was called! Consider using exec_safe_query instead. Called in file '{previous_frame[0]}' at line {previous_frame[1]} in function {previous_frame[2]}")
        self.conn.execute(str(querytoexecute))
        if fetchall:
            row = self.conn.fetchall()
        else:
            row = self.conn.fetchone()
        return row if row != () and row != "()" else None

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
