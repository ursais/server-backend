# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# this is needed to generate connection string
import pymssql
import sqlalchemy
from urllib.parse import quote_plus

from odoo import fields, models

assert pymssql


class BaseExternalDbsource(models.Model):
    """It provides logic for connection to a MSSQL data source."""

    _inherit = "base.external.dbsource"

    connector = fields.Selection(
        selection_add=[("mssql", "Microsoft SQL Server")], ondelete={"mssql": "cascade"}
    )
    PWD_STRING_MSSQL = "Password=%s;"

    def connection_close_mssql(self, connection):
        return connection.close()

    def connection_open_mssql(self):
        return self._connection_open_mssql()

    def execute_mssql(self, sqlquery, sqlparams, metadata):
        return self._execute_mssql(sqlquery, sqlparams, metadata)

    def _connection_open_mssql(self):
        conn_string = self.conn_string_full
        # Check if it's an ODBC connection string (starts with DRIVER=)
        if conn_string.strip().upper().startswith("DRIVER="):
            # Convert ODBC string to SQLAlchemy URL format using pyodbc
            # Format: mssql+pyodbc:///?odbc_connect=<encoded_connection_string>
            encoded_conn = quote_plus(conn_string)
            sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={encoded_conn}"
        else:
            # Use the connection string as-is (should be mssql+pymssql:// format)
            sqlalchemy_url = conn_string
        return sqlalchemy.create_engine(sqlalchemy_url).connect()

    def _execute_mssql(self, sqlquery, sqlparams, metadata):
        rows, cols = list(), list()
        for record in self:
            with record.connection_open() as connection:
                # Use exec_driver_sql for direct driver-level execution
                # This handles positional parameters (tuples) correctly with pyodbc
                if sqlparams is None:
                    cur = connection.exec_driver_sql(sqlquery)
                else:
                    # Convert tuple/list to tuple for exec_driver_sql
                    if isinstance(sqlparams, (tuple, list)):
                        cur = connection.exec_driver_sql(sqlquery, sqlparams)
                    elif isinstance(sqlparams, dict):
                        # For dict parameters, convert to tuple in order
                        # This assumes the query uses ? placeholders
                        # We'll need to extract values in order
                        # Note: This is a limitation - dict params need ordered values
                        params_tuple = tuple(sqlparams.values())
                        cur = connection.exec_driver_sql(sqlquery, params_tuple)
                    else:
                        # Single value
                        cur = connection.exec_driver_sql(sqlquery, (sqlparams,))
                
                if metadata:
                    cols = list(cur.keys())
                # If the query doesn't return rows, trying to get them anyway
                # will raise an exception `sqlalchemy.exc.ResourceClosedError`
                rows = [r for r in cur] if cur.returns_rows else []
        return rows, cols
