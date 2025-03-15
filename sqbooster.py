import json
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDatabase:
    """
    A simple database class to manage tables and perform CRUD operations.
    Each table corresponds to a "key" in the database.
    """

    def __init__(self, db_url):
        """
        Initialize the database connection.
        :param db_url: The database URL (e.g., 'sqlite:///example.db', 'mysql+pymysql://user:password@host/dbname')
        """
        self.engine = create_engine(db_url)
        self.metadata = MetaData(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_table_if_not_exists(self, table_name):
        """
        Create a table if it doesn't already exist.
        :param table_name: Name of the table to create.
        """
        try:
            if not self.engine.dialect.has_table(self.engine, table_name):
                table = Table(
                    table_name, self.metadata,
                    Column(
                        'id',
                        Integer,
                        primary_key=True,
                        autoincrement=True),
                    Column('value', String)
                )
                table.create(self.engine)
                logger.info(f"Table '{table_name}' has been created.")
            else:
                logger.info(f"Table '{table_name}' already exists.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create table '{table_name}': {e}")

    def read_data(self, key, default=None):
        """
        Read all data associated with a specific key (table).
        :param key: The name of the table (key) to read from.
        :param default: Default value to return if an error occurs.
        :return: List of values stored in the table, or the default value if an error occurs.
        """
        session = self.Session()
        try:
            self.create_table_if_not_exists(key)
            table = Table(key, self.metadata, autoload_with=self.engine)
            query_result = session.query(table.c.value).all()

            return [json.loads(row[0]) for row in query_result]
        except SQLAlchemyError as e:
            logger.error(f"Failed to read data from key '{key}': {e}")
            return default
        finally:
            session.close()

    def write_data(self, key, values):
        """
        Write data to a specific key (table). This will overwrite existing data.
        :param key: The name of the table (key) to write to.
        :param values: A list of values to store in the table.
        """
        session = self.Session()
        try:
            self.create_table_if_not_exists(key)
            table = Table(key, self.metadata, autoload_with=self.engine)
            session.execute(table.delete())
            for value in values:
                session.execute(table.insert().values(value=json.dumps(value)))
            session.commit()
            logger.info(f"Data successfully written to key '{key}'.")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to write data to key '{key}': {e}")
        finally:
            session.close()

    def update_data(self, key, values):
        """
        Add new data to a specific key (table) without overwriting existing data.
        :param key: The name of the table (key) to update.
        :param values: A list of values to add to the table.
        """
        session = self.Session()
        try:
            self.create_table_if_not_exists(key)
            table = Table(key, self.metadata, autoload_with=self.engine)
            for value in values:
                session.execute(table.insert().values(value=json.dumps(value)))
            session.commit()
            logger.info(f"Data successfully updated in key '{key}'.")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update data in key '{key}': {e}")
        finally:
            session.close()

    def delete_table(self, key):
        """
        Delete a specific table (key) from the database.
        :param key: The name of the table (key) to delete.
        """
        try:
            table = Table(key, self.metadata, autoload_with=self.engine)
            table.drop(self.engine)
            logger.info(f"Table '{key}' has been deleted.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete table '{key}': {e}")

    def search_data(self, key, search_value):
        """
        Search for a specific value in a table (key).
        :param key: The name of the table (key) to search in.
        :param search_value: The value to search for.
        :return: List of matching values, or an empty list if no matches are found.
        """
        session = self.Session()
        try:
            self.create_table_if_not_exists(key)
            table = Table(key, self.metadata, autoload_with=self.engine)
            query_result = session.query(table.c.value).filter(
                table.c.value.like(f"%{search_value}%")).all()

            return [json.loads(row[0]) for row in query_result]
        except SQLAlchemyError as e:
            logger.error(f"Failed to search data in key '{key}': {e}")
            return []
        finally:
            session.close()

    def list_tables(self):
        """
        List all tables (keys) in the database.
        :return: List of table names, or an empty list if an error occurs.
        """
        try:
            inspector = self.metadata.bind.dialect.get_table_names(
                bind=self.engine)
            return inspector
        except SQLAlchemyError as e:
            logger.error(f"Failed to list tables: {e}")
            return []
