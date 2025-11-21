# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# this is needed to generate connection string
import pymssql
import pyodbc
import sqlalchemy

from odoo import fields, models

assert pymssql


class BaseExternalDbsource(models.Model):
    """It provides logic for connection to a MSSQL data source."""

    _inherit = "base.external.dbsource"

    connector = fields.Selection(
        selection_add=[
            ("mssql", "Microsoft SQL Server"),
        ],
        ondelete={"mssql": "cascade"},
    )
    mssql_type = fields.Selection(
        selection=[
            ("alchemy", "SQLAlchemy"),
            ("pyodbc", "pyodbc"),
        ],
        string="MSSQL Connector Type",
        default="alchemy",
    )
    PWD_STRING_MSSQL = "Password=%s;"

    def connection_close_mssql(self, connection):
        return connection.close()

    def connection_open_mssql(self):
        return self._connection_open_mssql()

    def execute_mssql(self, sqlquery, sqlparams, metadata):
        return self._execute_mssql(sqlquery, sqlparams, metadata)

    def _connection_open_mssql(self):
        if self.mssql_type == "pyodbc":
            return pyodbc.connect(self.conn_string_full)
        else:  # alchemy
            return sqlalchemy.create_engine(self.conn_string_full).connect()

    def _execute_mssql(self, sqlquery, sqlparams, metadata):
        rows, cols = list(), list()
        for record in self:
            with record.connection_open() as connection:
                if record.mssql_type == "pyodbc":
                    cursor = connection.cursor()
                    if sqlparams is None:
                        cursor.execute(sqlquery)
                    else:
                        cursor.execute(sqlquery, sqlparams)
                    if metadata:
                        cols = [column[0] for column in cursor.description]
                    # rows = cursor.fetchall()
                    if (
                        cursor.description
                    ):  # description is only set for queries that return data
                        rows = cursor.fetchall()
                    else:
                        rows = None
                else:  # mssql-alchemy
                    if sqlparams is None:
                        cursor = connection.execute(sqlalchemy.text(sqlquery))
                    else:
                        cursor = connection.execute(
                            sqlalchemy.text(sqlquery), sqlparams
                        )
                    if metadata:
                        cols = list(cursor.keys())
                    # If the query doesn't return rows, trying to get them anyway
                    # will raise an exception `sqlalchemy.exc.ResourceClosedError`
                    rows = [r for r in cursor] if cursor.returns_rows else []
        return rows, cols
