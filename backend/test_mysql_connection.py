import os
import pymysql
import pytest

@pytest.fixture(scope='module')
def mysql_connection():
    # Récupérer les variables d'environnement pour la connexion MySQL
    db_host = os.getenv('MYSQL_HOST', '127.0.0.1')
    db_user = os.getenv('MYSQL_USER', 'test_user')
    db_password = os.getenv('MYSQL_PASSWORD', 'test_password')
    db_name = os.getenv('MYSQL_DATABASE', 'test_db')
    db_port = int(os.getenv('MYSQL_PORT', 3306))

    conn = None
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )
        yield conn
    except pymysql.Error as e:
        pytest.fail(f"Impossible de se connecter à MySQL: {e}")
    finally:
        if conn:
            conn.close()

def test_mysql_connection_successful(mysql_connection):
    # Si la fixture mysql_connection se termine sans erreur, la connexion est réussie
    assert mysql_connection is not None
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result == (1,)
