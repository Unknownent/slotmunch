import os
class Config:
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "canteen_system")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_SSL = os.environ.get("MYSQL_SSL", "false").lower() == "true"