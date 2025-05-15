#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definiciones de funcionalidades comunes en proyectos de software.

Este módulo contiene las definiciones y patrones para detectar
funcionalidades comunes como autenticación, bases de datos, etc.
"""

from typing import Dict, List, Set, Pattern
import re

# Patrones para detectar funcionalidades comunes en el código

# Autenticación y seguridad
AUTH_PATTERNS = {
    'files': [
        r'auth', r'login', r'security', r'user', r'credential', r'password', 
        r'jwt', r'oauth', r'permission', r'role', r'identity', r'session',
        r'firebase.*auth', r'cognito', r'authentication', r'sha\d+', r'hash'
    ],
    'imports': [
        r'jwt', r'bcrypt', r'passlib', r'firebase_auth', r'passport', 
        r'auth0', r'django.contrib.auth', r'flask_login', r'flask_security',
        r'spring.*security', r'pyotp', r'authlib', r'microsoft.*identity',
        r'google.*auth', r'amazon.*cognito'
    ],
    'code_patterns': [
        r'auth[._]', r'login', r'authenticate', r'authorization', r'hasRole', 
        r'isAuthenticated', r'verify.*password', r'check.*password', r'session[._]',
        r'token[._]', r'jwt[._]', r'useAuth', r'currentUser', r'signin', r'signup',
        r'firebase[._]auth', r'AuthProvider', r'[aA]uth.*[pP]rovider', r'hash.*password'
    ],
    'config_keys': [
        r'auth', r'jwt', r'secret.*key', r'api.*key', r'token', r'firebase', 
        r'oauth', r'auth0', r'cognito', r'ALLOWED_HOSTS', r'CORS', 
        r'SESSION', r'COOKIE', r'KEY', r'AUTH_USER_MODEL', r'AUTHENTICATION_BACKENDS'
    ]
}

# Base de datos
DATABASE_PATTERNS = {
    'files': [
        r'db', r'database', r'model', r'entity', r'repository', r'schema',
        r'migration', r'dao', r'orm', r'mongo', r'sql', r'postgres', r'mysql',
        r'sqlite', r'redis', r'sequelize', r'prisma', r'knex', r'typeorm'
    ],
    'imports': [
        r'django.db', r'sqlalchemy', r'mongoose', r'sequelize', r'typeorm',
        r'knex', r'prisma', r'sqlite3', r'redis', r'mongodb', r'pymongo',
        r'psycopg\d?', r'mysql', r'postgres', r'hibernate', r'spring.*data',
        r'spring.*jdbc', r'entity.*framework', r'peewee', r'tortoise'
    ],
    'code_patterns': [
        r'database', r'db\.', r'Model', r'Schema', r'repository', r'query',
        r'findOne', r'findAll', r'findBy', r'save\(', r'select ', r'insert ',
        r'update ', r'delete from', r'migration', r'table', r'column',
        r'SQL', r'mongo', r'postgres', r'useQuery', r'useMutation',
        r'createConnection', r'connect\(.*mongo', r'connect\(.*sql',
        r'createTable', r'addColumn', r'models\.', r'model\(', r'entity\(',
        r'collection\(', r'document\('
    ],
    'config_keys': [
        r'DATABASE', r'DB_', r'MONGO', r'POSTGRES', r'MYSQL', r'SQLITE', r'REDIS',
        r'connection', r'username', r'password', r'host', r'port', r'database',
        r'URL', r'URI', r'DSN', r'DB_NAME', r'DB_USER', r'DB_PASS', r'DB_HOST',
        r'SQLALCHEMY'
    ]
}

# APIs y integraciones
API_PATTERNS = {
    'files': [
        r'api', r'controller', r'route', r'endpoint', r'service', r'client',
        r'rest', r'http', r'graphql', r'grpc', r'webhook', r'openapi', r'swagger'
    ],
    'imports': [
        r'axios', r'request', r'fetch', r'http', r'rest', r'restful',
        r'express', r'fastapi', r'flask', r'django.*rest_framework',
        r'graphql', r'apollo', r'grpc', r'protobuf', r'aiohttp', r'requests',
        r'retrofit', r'feign', r'resttemplate', r'spring.*rest',
        r'jersey', r'openapi', r'swagger', r'postman'
    ],
    'code_patterns': [
        r'fetch\(', r'http\.', r'get\(.*url', r'post\(.*url', r'put\(.*url', r'delete\(.*url',
        r'api', r'controller', r'endpoint', r'@route', r'@api', r'router',
        r'@controller', r'@requestmapping', r'@getmapping', r'@postmapping',
        r'return.*json', r'return.*response', r'response\.json', r'return.*status',
        r'useQuery', r'useMutation', r'Response\.ok', r'Response\.error',
        r'handleRequest', r'handleResponse', r'apiClient', r'apiService'
    ],
    'config_keys': [
        r'API_', r'URL', r'ENDPOINT', r'REST', r'HTTP', r'HOST', r'PORT',
        r'BASE_URL', r'SERVICE', r'CLIENT', r'TOKEN', r'KEY', r'TIMEOUT',
        r'RATE_LIMIT', r'GRAPHQL', r'SWAGGER', r'OPENAPI'
    ]
}

# Frontend / UI
FRONTEND_PATTERNS = {
    'files': [
        r'component', r'view', r'page', r'layout', r'template', r'theme',
        r'style', r'css', r'scss', r'sass', r'less', r'ui', r'interface',
        r'react', r'vue', r'angular', r'svelte', r'html', r'jsx', r'tsx'
    ],
    'imports': [
        r'react', r'react-dom', r'angular', r'vue', r'svelte', r'preact',
        r'component', r'material-ui', r'antd', r'bootstrap', r'tailwind',
        r'styled-components', r'emotion', r'chakra-ui', r'primereact', r'vuetify',
        r'@angular/core', r'@angular/material', r'@angular/router', 
        r'@mui/material', r'@chakra-ui', r'@emotion'
    ],
    'code_patterns': [
        r'component', r'render', r'return.*jsx', r'className', r'style=',
        r'<div', r'<span', r'<p', r'useState', r'useEffect', r'useContext',
        r'props', r'@Component', r'template', r'v-if', r'v-for', r'v-model',
        r'@Input', r'@Output', r'onChange', r'onClick', r'onSubmit',
        r'import.*css', r'import.*scss', r'import.*less'
    ],
    'config_keys': [
        r'THEME', r'STYLE', r'UI', r'COLOR', r'FONT', r'LAYOUT',
        r'REACT_APP_', r'VUE_APP_', r'NG_', r'VITE_', r'NEXT_PUBLIC_',
        r'GATSBY_', r'PUBLIC_URL', r'ASSET_PREFIX'
    ]
}

# Pruebas automatizadas
TEST_PATTERNS = {
    'files': [
        r'test', r'spec', r'\_\_tests\_\_', r'mocha', r'jasmine', r'jest',
        r'cypress', r'e2e', r'selenium', r'fixture', r'mock', r'stub'
    ],
    'imports': [
        r'test', r'jest', r'mocha', r'chai', r'assert', r'expect',
        r'unittest', r'pytest', r'testing', r'junit', r'testng', r'mockito',
        r'powerMock', r'sinon', r'cypress', r'selenium', r'playwright',
        r'vitest', r'@testing-library', r'supertest'
    ],
    'code_patterns': [
        r'test\(', r'it\(', r'describe\(', r'expect\(', r'assert',
        r'mock', r'spy\(', r'stub\(', r'beforeEach', r'afterEach',
        r'@Test', r'@Before', r'@After', r'@Mock', r'assertEquals',
        r'should\.', r'should\(', r'assert\.', r'toBe\(', r'toEqual\(',
        r'pytest', r'unittest', r'testcase', r'cy\.'
    ],
    'config_keys': [
        r'TEST_', r'JEST', r'MOCHA', r'CHAI', r'CYPRESS', r'SELENIUM',
        r'FIXTURE', r'MOCK', r'E2E', r'INTEGRATION', r'UNIT',
        r'COVERAGE', r'CI', r'testMatch', r'testRegex', r'setupFilesAfterEnv'
    ]
}

# Recopilación de todas las funcionalidades
FUNCTIONALITY_PATTERNS = {
    'authentication': AUTH_PATTERNS,
    'database': DATABASE_PATTERNS,
    'api': API_PATTERNS,
    'frontend': FRONTEND_PATTERNS,
    'tests': TEST_PATTERNS
}

# Pesos para calcular la confianza de detección
DETECTION_WEIGHTS = {
    'files': 5,       # Nombres de archivos y directorios
    'imports': 10,    # Importaciones en el código
    'code_patterns': 3,  # Patrones en el código
    'config_keys': 8   # Configuraciones
}

# Umbral de confianza para confirmar la presencia de una funcionalidad
CONFIDENCE_THRESHOLD = 15