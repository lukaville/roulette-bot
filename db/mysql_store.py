import mysql.connector

# User states
# IDLE — disconnected and not searching for new users
# SEARCH — searching for new users
STATE_IDLE = None
STATE_SEARCH = -1

# Database schema (create table statements)
DB_SCHEMA = ("CREATE TABLE IF NOT EXISTS `users` ( "
             "`id` INT(11) NOT NULL, "
             "`chat_with` INT(11) DEFAULT NULL, "
             "PRIMARY KEY (`id`), "
             "UNIQUE KEY `id_UNIQUE` (`id`) "
             ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci; ")


def connect(fn):
    """
    This decorator gets MySQL connection and
    passes connection as kwarg 'connection'
    """

    def wrap_function(self, *args, **kwargs):
        connection = self._get_connection()
        kwargs['connection'] = connection
        result = fn(self, *args, **kwargs)
        connection.close()
        return result

    return wrap_function


def parse_user(row):
    """
    Convert MySQL row to user dict
    :param row: tuple
    :return: user dict
    """
    if row is None:
        return None

    (user_id, chat_with) = row
    return {
        'user_id': user_id,
        'chat_with': chat_with
    }


def update_user(cursor, user_id, chat_with):
    """
    Update user information in database
    :param cursor: MySQL cursor
    :param user_id: user identifier
    :param chat_with: chat with parameter
    """
    set_user = ("UPDATE users "
                "SET chat_with=%(chat_with)s "
                "WHERE id=%(user_id)s")

    cursor.execute(set_user, {
        'user_id': user_id,
        'chat_with': chat_with
    })


class MySQLStore(object):
    def __init__(self, config):
        self.config = {
            'user': config['MYSQL_USER'],
            'password': config['MYSQL_PASSWORD'],
            'host': config['MYSQL_HOST'],
        }

        self.database = config['MYSQL_DATABASE']
        self.pool_size = config['MYSQL_CONNECTION_POOL_SIZE']

        self.create_db()

    def _get_connection(self):
        # TODO: add pooling
        """
        Connects to MySQL or gets connection from pool
        :return: MySQL connection (maybe pooled)
        """
        return mysql.connector.connect(
            **self.config
        )

    def create_db(self):
        """
        Creates MySQL database with name specified in config
        """
        connection = mysql.connector.connect(**self.config)
        cursor = connection.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS {}'.format(self.database))
        cursor.close()
        connection.close()

        self.config['database'] = self.database
        self._create_schema()

    @connect
    def _create_schema(self, connection):
        """
        Imports MySQL database schema (tables) to actual db
        """
        cursor = connection.cursor()
        cursor.execute(DB_SCHEMA)
        cursor.close()

    @connect
    def drop_db(self, connection):
        """
        Drops database specified in config, useful for testing
        """
        cursor = connection.cursor()
        cursor.execute('DROP DATABASE {}'.format(self.database), {
            'db': self.config['database']
        })
        cursor.close()

    @connect
    def get_user(self, user_id, connection):
        """
        Get user object from database
        :param user_id: user identifier
        :return: user dict
        """
        cursor = connection.cursor()

        query = ("SELECT id, chat_with FROM users "
                 "WHERE id = %(user_id)s")
        cursor.execute(query, {'user_id': user_id})

        row = cursor.fetchone()
        user = parse_user(row)

        cursor.close()
        return user

    @connect
    def create_user(self, user_id, connection):
        """
        Creates new user with SEARCH state
        :param user_id: user identifier
        :return: new user dict
        """
        new_user = {
            'user_id': user_id,
            'chat_with': STATE_SEARCH
        }

        cursor = connection.cursor()
        add_user = ("INSERT INTO users "
                    "(id, chat_with) "
                    "VALUES (%(user_id)s, %(chat_with)s)")

        cursor.execute(add_user, new_user)
        connection.commit()
        cursor.close()

        return new_user

    @connect
    def disconnect(self, user_id, paired_user_id, connection):
        """
        If paired_user_id specified — unpairs users and
        sets IDLE state to paired user and SEARCH to first user
        If only user_id specified — sets IDLE state to him
        :param user_id: first user identifier
        :param paired_user_id: paired user identifier
        """
        cursor = connection.cursor()

        if paired_user_id is None:
            update_user(cursor, user_id, STATE_IDLE)
        else:
            update_user(cursor, user_id, STATE_SEARCH)
            update_user(cursor, paired_user_id, STATE_IDLE)

        connection.commit()
        cursor.close()

    @connect
    def pair_user(self, user_id, choose_user, connection):
        """
        Find pair for user
        :param user_id: user identifier
        :param choose_user: function for choosing user
               from list (argument — list of users, return one user)
        :return: founded user id if user paired successfully
                 else returns None
        """
        cursor = connection.cursor()

        founded_user_id = None

        cursor.execute(
            ("SELECT id, chat_with FROM users "
             "WHERE chat_with = %(chat_with)s AND id != %(user_id)s"),
            {'user_id': user_id, 'chat_with': STATE_SEARCH})
        free_users = [parse_user(r) for r in cursor.fetchall()]

        if len(free_users) > 0:
            second_user_id = choose_user(free_users)['user_id']
            update_user(cursor, user_id, second_user_id)
            update_user(cursor, second_user_id, user_id)
            founded_user_id = second_user_id

        connection.commit()
        cursor.close()

        return founded_user_id
