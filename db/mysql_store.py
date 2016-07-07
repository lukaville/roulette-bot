import mysql.connector


def connect(fn):
    def wrap_function(self, *args, **kwargs):
        connection = self._get_connection()
        kwargs['connection'] = connection
        result = fn(self, *args, **kwargs)
        connection.close()
        return result

    return wrap_function


def parse_user(row):
    if row is None:
        return None

    (user_id, name, chat_with) = row
    return {
        'user_id': user_id,
        'name': name,
        'chat_with': chat_with
    }


class MySQLStore(object):
    def __init__(self, mysql_config):
        self.config = {
            'user': mysql_config['MYSQL_USER'],
            'password': mysql_config['MYSQL_PASSWORD'],
            'host': mysql_config['MYSQL_HOST'],
            'database': mysql_config['MYSQL_DATABASE']
        }

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    @connect
    def get_user(self, user_id, connection):
        cursor = connection.cursor()

        query = ("SELECT id, name, chat_with FROM users "
                 "WHERE id = %(user_id)s")
        cursor.execute(query, {'user_id': user_id})

        row = cursor.fetchone()
        user = parse_user(row)

        cursor.close()
        return user
