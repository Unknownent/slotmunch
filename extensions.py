import pymysql
import pymysql.cursors
from config import Config
def get_db_connection():
    ssl_args = {"ssl": {"ssl": True}} if Config.MYSQL_SSL else {}
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        **ssl_args,
    )