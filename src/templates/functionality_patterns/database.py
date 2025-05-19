#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Patrones avanzados para detección de funcionalidades de bases de datos.

Este módulo contiene patrones específicos para la detección
de funcionalidades de bases de datos en proyectos.
"""

from typing import Dict, List, Any

# Patrones avanzados para bases de datos
DATABASE_PATTERNS_ADVANCED = {
    'files': {
        'simple': [
            r'db', r'database', r'model', r'entity', r'repository', r'schema',
            r'migration', r'dao', r'orm', r'mongo', r'sql', r'postgres', r'mysql',
            r'sqlite', r'redis', r'sequelize', r'prisma', r'knex', r'typeorm'
        ],
        'weighted': {
            r'db\.': 8,
            r'database\.': 10,
            r'model\.': 7,
            r'entity\.': 8,
            r'repository\.': 9,
            r'schema\.': 8,
            r'migration\.': 10,
            r'dao\.': 9,
            r'orm\.': 10,
            r'sequelize\.': 10,
            r'prisma\.': 10,
            r'typeorm\.': 10,
            r'mongoose\.': 10,
            r'knex\.': 10
        }
    },
    'imports': {
        'simple': [
            r'django.db', r'sqlalchemy', r'mongoose', r'sequelize', r'typeorm',
            r'knex', r'prisma', r'sqlite3', r'redis', r'mongodb', r'pymongo',
            r'psycopg\d?', r'mysql', r'postgres', r'hibernate', r'spring.*data',
            r'spring.*jdbc', r'entity.*framework', r'peewee', r'tortoise'
        ],
        'weighted': {
            r'django\.db': 10,
            r'sqlalchemy': 10,
            r'mongoose': 10,
            r'sequelize': 10,
            r'typeorm': 10,
            r'knex': 10,
            r'prisma': 10,
            r'sqlite3': 9,
            r'redis': 9,
            r'mongodb': 9,
            r'pymongo': 9,
            r'psycopg': 9,
            r'mysql': 9,
            r'postgres': 9,
            r'hibernate': 10,
            r'spring.*data': 10,
            r'spring.*jdbc': 10,
            r'entity.*framework': 10,
            r'peewee': 10,
            r'tortoise': 10,
            r'objection': 10,
            r'bookshelf': 9,
            r'firestore': 9,
            r'realm': 9,
            r'dynamodb': 9,
            r'cassandra': 9,
            r'couchdb': 9
        }
    },
    'code_patterns': {
        'simple': [
            r'database', r'db\.', r'Model', r'Schema', r'repository', r'query',
            r'findOne', r'findAll', r'findBy', r'save\(', r'select ', r'insert ',
            r'update ', r'delete from', r'migration', r'table', r'column',
            r'SQL', r'mongo', r'postgres', r'useQuery', r'useMutation',
            r'createConnection', r'connect\(.*mongo', r'connect\(.*sql',
            r'createTable', r'addColumn', r'models\.', r'model\(', r'entity\(',
            r'collection\(', r'document\('
        ],
        'weighted': {
            r'database\.(query|execute)': 10,
            r'db\.(query|execute)': 10,
            r'Model\.find': 10,
            r'Model\.create': 10,
            r'Model\.update': 10,
            r'Model\.delete': 10,
            r'repository\.(find|save|delete)': 10,
            r'SELECT\s+.*\s+FROM': 10,
            r'INSERT\s+INTO': 10,
            r'UPDATE\s+.*\s+SET': 10,
            r'DELETE\s+FROM': 10,
            r'CREATE\s+TABLE': 10,
            r'ALTER\s+TABLE': 10,
            r'DROP\s+TABLE': 10,
            r'JOIN': 8,
            r'WHERE': 7,
            r'GROUP\s+BY': 8,
            r'ORDER\s+BY': 7,
            r'connection\.query': 10,
            r'migrate\(': 10,
            r'rollback\(': 10,
            r'findById': 9,
            r'findByPk': 9,
            r'findOne': 9,
            r'findAll': 9,
            r'save\(': 8,
            r'commit\(': 8,
            r'transaction\(': 10,
            r'mongoose\.Schema': 10,
            r'mongoose\.model': 10,
            r'Schema\.define': 10,
            r'createIndex': 9,
            r'entity.*relationship': 10,
            r'OneToMany': 10,
            r'ManyToOne': 10,
            r'ManyToMany': 10,
            r'column\(': 9,
            r'foreignKey': 9
        }
    },
    'config_keys': {
        'simple': [
            r'DATABASE', r'DB_', r'MONGO', r'POSTGRES', r'MYSQL', r'SQLITE', r'REDIS',
            r'connection', r'username', r'password', r'host', r'port', r'database',
            r'URL', r'URI', r'DSN', r'DB_NAME', r'DB_USER', r'DB_PASS', r'DB_HOST',
            r'SQLALCHEMY'
        ],
        'weighted': {
            r'DATABASE_URL': 10,
            r'DB_CONNECTION': 10,
            r'DB_HOST': 10,
            r'DB_PORT': 10,
            r'DB_DATABASE': 10,
            r'DB_USERNAME': 10,
            r'DB_PASSWORD': 10,
            r'MONGO_URI': 10,
            r'REDIS_URL': 10,
            r'POSTGRES_.*': 10,
            r'MYSQL_.*': 10,
            r'SQLITE_.*': 10,
            r'SQLALCHEMY_DATABASE_URI': 10,
            r'SQLALCHEMY_TRACK_MODIFICATIONS': 10,
            r'TYPEORM_.*': 10,
            r'PRISMA_.*': 10,
            r'SEQUELIZE_.*': 10,
            r'HIBERNATE_.*': 10,
            r'DATABASE_ENGINE': 10,
            r'DATABASE_NAME': 10,
            r'DATABASE_USER': 10,
            r'DATABASE_PASSWORD': 10,
            r'DATABASE_HOST': 10,
            r'DATABASE_PORT': 10
        }
    },
    # Framework específicos
    'frameworks': {
        'django': [
            r'django\.db', r'models\.Model', r'makemigrations', r'migrate',
            r'CharField', r'IntegerField', r'DateField', r'ForeignKey', r'OneToOneField',
            r'ManyToManyField', r'objects\.filter', r'objects\.get', r'objects\.create'
        ],
        'sqlalchemy': [
            r'sqlalchemy', r'Base', r'Column', r'Integer', r'String', r'ForeignKey',
            r'relationship', r'session', r'query', r'execute', r'commit', r'rollback',
            r'alembic', r'migration', r'upgrade', r'downgrade'
        ],
        'mongoose': [
            r'mongoose', r'Schema', r'model', r'connect', r'find', r'findOne',
            r'findById', r'save', r'updateOne', r'deleteOne', r'populate'
        ],
        'sequelize': [
            r'sequelize', r'Model', r'DataTypes', r'belongsTo', r'hasMany', r'hasOne',
            r'belongsToMany', r'sync', r'query', r'transaction', r'migration'
        ],
        'typeorm': [
            r'typeorm', r'Entity', r'PrimaryGeneratedColumn', r'Column', r'OneToMany',
            r'ManyToOne', r'ManyToMany', r'Repository', r'getRepository', r'migration'
        ],
        'hibernate': [
            r'hibernate', r'Entity', r'Table', r'Column', r'Id', r'GeneratedValue',
            r'OneToMany', r'ManyToOne', r'ManyToMany', r'JoinColumn', r'CascadeType',
            r'SessionFactory', r'Session', r'Query', r'Criteria', r'Transaction'
        ],
        'spring-data': [
            r'spring\.data', r'Repository', r'JpaRepository', r'CrudRepository',
            r'MongoRepository', r'findById', r'findAll', r'save', r'deleteById',
            r'@Query', r'@Entity', r'@Table', r'@Column', r'@Id'
        ],
        'entity-framework': [
            r'entity.*framework', r'DbContext', r'DbSet', r'OnModelCreating',
            r'HasOne', r'WithMany', r'HasMany', r'WithOne', r'Entity', r'Migration',
            r'Add-Migration', r'Update-Database'
        ],
        'prisma': [
            r'prisma', r'PrismaClient', r'schema\.prisma', r'model', r'generator',
            r'datasource', r'migrate', r'introspect', r'generate'
        ]
    },
    # Tipos de bases de datos
    'db_types': {
        'relational': [
            r'sql', r'mysql', r'postgres', r'sqlite', r'oracle', r'sqlserver',
            r'relational', r'foreign.*key', r'primary.*key', r'join', r'transaction',
            r'acid'
        ],
        'document': [
            r'mongo', r'document', r'nosql', r'firebase.*firestore', r'cosmos.*db',
            r'couchdb', r'collection', r'document', r'aggregate'
        ],
        'key-value': [
            r'redis', r'memcache', r'etcd', r'dynamodb', r'key.*value', r'cache',
            r'set', r'get', r'hset', r'hget'
        ],
        'graph': [
            r'neo4j', r'janus.*graph', r'graph.*db', r'vertex', r'edge',
            r'node', r'relationship', r'traversal', r'cypher'
        ],
        'time-series': [
            r'influx.*db', r'time.*series', r'time.*stamped', r'prometheus',
            r'grafana', r'metric', r'series'
        ],
        'object': [
            r'realm', r'object.*db', r'embedded.*db', r'objectbox', r'object.*store',
            r'persistable', r'managed.*object'
        ]
    },
    # Operaciones específicas
    'operations': {
        'crud': [
            r'create', r'read', r'update', r'delete', r'insert', r'select',
            r'find', r'save', r'remove', r'get.*by.*id'
        ],
        'migration': [
            r'migration', r'migrate', r'rollback', r'up', r'down', r'alembic',
            r'flyway', r'liquibase', r'schema.*change'
        ],
        'transaction': [
            r'transaction', r'commit', r'rollback', r'begin', r'atomic',
            r'savepoint', r'isolation.*level'
        ],
        'indexing': [
            r'index', r'unique.*index', r'compound.*index', r'createIndex',
            r'indexBy', r'fulltext', r'search'
        ]
    }
}

# Mapeo de frameworks a tipos de bases de datos comúnmente utilizadas
DATABASE_FRAMEWORK_TYPES = {
    'django': ['relational'],
    'flask+sqlalchemy': ['relational'],
    'express+mongoose': ['document'],
    'express+sequelize': ['relational'],
    'spring+hibernate': ['relational'],
    'spring+mongodb': ['document'],
    'react+firebase': ['document', 'key-value'],
    'laravel': ['relational'],
    'rails': ['relational'],
    'fastapi+sqlalchemy': ['relational'],
    'fastapi+motor': ['document'],
    'go+gorm': ['relational'],
    'go+mongo-driver': ['document']
}
