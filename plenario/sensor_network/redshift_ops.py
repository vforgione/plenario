from sqlalchemy import text

from plenario.database import redshift_engine


def create_network_table(network_name):
    op = text('CREATE TABLE {} ('
              '"nodeId" VARCHAR NOT NULL,'
              'datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,'
              'PRIMARY KEY ("nodeId", datetime))'.format(network_name))
    redshift_engine.execute(op)


def add_column(network_name, column_name, column_type):
    op = text('ALTER TABLE {}'
              'ADD COLUMN {} {}'
              'DEFAULT NULL'.format(network_name, column_name, column_type))
    redshift_engine.execute(op)


create_network_table('ArrayOfThings')
add_column('ArrayOfThings', 'temperature__DB110', 'decimal')