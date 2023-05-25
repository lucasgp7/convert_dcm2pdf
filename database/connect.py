import configparser
import psycopg2

def get_mysql_config():
    config = configparser.ConfigParser()
    config.read('config.properties')

    db_host = config.get('mysql', 'host')
    db_user = config.get('mysql', 'user')
    db_password = config.get('mysql', 'password')
    db_database = config.get('mysql', 'database')

    return db_host, db_user, db_password, db_database

def get_postgresql_config():
    config = configparser.ConfigParser()
    config.read('config.properties')

    postgresql_host = config.get('postgresql', 'postgresql.host')
    postgresql_user = config.get('postgresql', 'postgresql.user')
    postgresql_password = config.get('postgresql', 'postgresql.password')
    postgresql_database = config.get('postgresql', 'postgresql.database')

    return postgresql_host, postgresql_user, postgresql_password, postgresql_database

