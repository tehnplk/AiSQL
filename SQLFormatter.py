#!/usr/bin/env python3
"""
MySQL SQL Query Formatter MCP Server using FastMCP

This server provides a single tool for formatting MySQL SQL queries.
"""

import re
from sqlparse import format as sql_format


class MySQLFormatter:
    """MySQL-specific SQL formatter"""

    def __init__(self):
        self.mysql_keywords = {
            "AUTOCOMMIT",
            "AUTO_INCREMENT",
            "BIGINT",
            "BINARY",
            "BIT",
            "BLOB",
            "BOOLEAN",
            "CHAR",
            "CHARACTER",
            "DATE",
            "DATETIME",
            "DECIMAL",
            "DOUBLE",
            "ENUM",
            "FLOAT",
            "FULLTEXT",
            "GEOMETRY",
            "INT",
            "INTEGER",
            "JSON",
            "LONGBLOB",
            "LONGTEXT",
            "MEDIUMBLOB",
            "MEDIUMINT",
            "MEDIUMTEXT",
            "NUMERIC",
            "REAL",
            "SET",
            "SMALLINT",
            "TEXT",
            "TIME",
            "TIMESTAMP",
            "TINYBLOB",
            "TINYINT",
            "TINYTEXT",
            "UNSIGNED",
            "VARBINARY",
            "VARCHAR",
            "YEAR",
            "ZEROFILL",
        }

    def format_sql(
        self,
        sql: str,
        keyword_case: str = "upper",
        identifier_case: str = "lower",
        strip_comments: bool = False,
        reindent: bool = True,
        indent_width: int = 2,
        wrap_after: int = 0,
        comma_first: bool = False,
        use_space_around_operators: bool = True,
    ) -> str:
        """Format MySQL SQL query with specified options"""
        try:
            # Apply basic SQL formatting
            formatted = sql_format(
                sql,
                keyword_case=keyword_case,
                identifier_case=identifier_case,
                strip_comments=strip_comments,
                reindent=reindent,
                indent_width=indent_width,
                wrap_after=wrap_after,
                comma_first=comma_first,
                use_space_around_operators=use_space_around_operators,
            )

            # Apply MySQL-specific formatting
            formatted = self._apply_mysql_formatting(formatted, keyword_case)

            return formatted.strip()

        except Exception as e:
            raise ValueError(f"Error formatting MySQL SQL: {str(e)}")

    def _apply_mysql_formatting(self, sql: str, keyword_case: str) -> str:
        """Apply MySQL-specific formatting rules"""
        # Handle MySQL-specific keywords
        for keyword in self.mysql_keywords:
            if keyword_case == "upper":
                pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
                sql = pattern.sub(keyword.upper(), sql)
            elif keyword_case == "lower":
                pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
                sql = pattern.sub(keyword.lower(), sql)

        # Handle MySQL backticks for identifiers (preserve them)
        sql = re.sub(r"`([^`]+)`", r"`\1`", sql)

        # Handle MySQL-specific functions
        mysql_functions = [
            "CONCAT",
            "SUBSTRING",
            "IFNULL",
            "COALESCE",
            "UNIX_TIMESTAMP",
            "FROM_UNIXTIME",
        ]
        for func in mysql_functions:
            if keyword_case == "upper":
                pattern = re.compile(r"\b" + re.escape(func) + r"\b", re.IGNORECASE)
                sql = pattern.sub(func.upper(), sql)
            elif keyword_case == "lower":
                pattern = re.compile(r"\b" + re.escape(func) + r"\b", re.IGNORECASE)
                sql = pattern.sub(func.lower(), sql)

        # Handle MySQL comment styles
        sql = re.sub(r"#([^\n]*)", r"-- \1", sql)  # Convert # comments to -- comments

        return sql
