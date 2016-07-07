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

    (user_id, chat_with) = row
    return {
        'user_id': user_id,
        'chat_with': chat_with
    }


def create_user(cursor, user_id):
    add_user = ("INSERT INTO users "
                "(id, chat_with) "
                "VALUES (%(user_id)s, %(chat_with)s)")

    cursor.execute(add_user, {
        'user_id': user_id,
        'chat_with': None
    })


def update_user(cursor, user_id, chat_with):
    set_user = ("UPDATE users "
                "SET chat_with=%(chat_with)s "
                "WHERE id=%(user_id)s")

    cursor.execute(set_user, {
        'user_id': user_id,
        'chat_with': chat_with
    })


def find_couple(cursor, user_id):
    cursor.execute(
        ("SELECT id, chat_with FROM users "
         "WHERE chat_with IS NULL AND id != %(user_id)s"),
        {'user_id': user_id})
    free_users = [parse_user(r) for r in cursor.fetchall()]

    if len(free_users) > 0:
        second_user_id = free_users[0]['user_id']
        update_user(cursor, user_id, second_user_id)
        update_user(cursor, second_user_id, user_id)
        return second_user_id
    else:
        return None


class MySQLStore(object):
    def __init__(self, config):
        self.config = {
            'user': config['MYSQL_USER'],
            'password': config['MYSQL_PASSWORD'],
            'host': config['MYSQL_HOST'],
            'database': config['MYSQL_DATABASE'],
        }
        self.pool_size = config['MYSQL_CONNECTION_POOL_SIZE']

    def _get_connection(self):
        return mysql.connector.connect(
            pool_name='pool',
            pool_size=self.pool_size,
            **self.config
        )

    @connect
    def get_user(self, user_id, connection):
        cursor = connection.cursor()

        query = ("SELECT id, chat_with FROM users "
                 "WHERE id = %(user_id)s")
        cursor.execute(query, {'user_id': user_id})

        row = cursor.fetchone()
        user = parse_user(row)

        cursor.close()
        return user

    @connect
    def roulette(self, user_id, connection):
        cursor = connection.cursor()

        user = self.get_user(user_id)

        if user is None:
            create_user(cursor, user_id)

        founded_user_id = find_couple(cursor, user_id)

        connection.commit()
        cursor.close()

        return founded_user_id
