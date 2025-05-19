#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Patrones avanzados para detección de funcionalidades de autenticación.

Este módulo contiene patrones específicos para la detección
de funcionalidades de autenticación y autorización en proyectos.
"""

from typing import Dict, List, Any

# Patrones avanzados para autenticación
AUTH_PATTERNS_ADVANCED = {
    'files': {
        'simple': [
            r'auth', r'login', r'security', r'user', r'credential', r'password',
            r'jwt', r'oauth', r'permission', r'role', r'identity', r'session',
            r'firebase.*auth', r'cognito', r'authentication', r'sha\d+', r'hash'
        ],
        'weighted': {
            r'auth\.': 8,
            r'login\.': 8,
            r'security\.': 7,
            r'user\.': 5,
            r'authentication\.': 10,
            r'oauth\.': 10,
            r'jwt\.': 10,
            r'password\.': 7,
            r'credential\.': 8,
            r'session\.': 6,
            r'permission\.': 7,
            r'role\.': 6,
            r'identity\.': 7,
        }
    },
    'imports': {
        'simple': [
            r'jwt', r'bcrypt', r'passlib', r'firebase_auth', r'passport', 
            r'auth0', r'django.contrib.auth', r'flask_login', r'flask_security',
            r'spring.*security', r'pyotp', r'authlib', r'microsoft.*identity',
            r'google.*auth', r'amazon.*cognito'
        ],
        'weighted': {
            r'jwt': 9,
            r'bcrypt': 10,
            r'passlib': 10,
            r'firebase_auth': 10,
            r'passport': 9,
            r'auth0': 10,
            r'django\.contrib\.auth': 10,
            r'flask_login': 10,
            r'flask_security': 10,
            r'spring.*security': 10,
            r'next-auth': 10,
            r'@auth0/': 10,
            r'firebase/auth': 10,
            r'microsoft.*identity': 10,
            r'google.*auth': 10,
            r'amazon.*cognito': 10,
            r'keycloak': 10,
            r'okta': 10,
            r'azure.*ad': 10,
            r'pytorch': -5,  # Palabra para reducir falsos positivos
            r'tensorflow': -5,
            r'numpy': -3,
        }
    },
    'code_patterns': {
        'simple': [
            r'auth[._]', r'login', r'authenticate', r'authorization', r'hasRole', 
            r'isAuthenticated', r'verify.*password', r'check.*password', r'session[._]',
            r'token[._]', r'jwt[._]', r'useAuth', r'currentUser', r'signin', r'signup',
            r'firebase[._]auth', r'AuthProvider', r'[aA]uth.*[pP]rovider', r'hash.*password'
        ],
        'weighted': {
            r'authenticate\(': 10,
            r'login\(': 9,
            r'logout\(': 9,
            r'signIn\(': 9,
            r'signOut\(': 9,
            r'register\(': 8,
            r'isAuthenticated\(\)': 10,
            r'hasRole\(': 10,
            r'hasPermission\(': 10,
            r'verify(Password|Token)': 10,
            r'hash(Password)': 10,
            r'decrypt(Password|Token)': 10,
            r'currentUser': 8,
            r'generat(e|ing)Token': 9,
            r'validateToken': 9,
            r'refreshToken': 9,
            r'useAuth': 10,
            r'AuthContext': 10,
            r'(get|set)Cookie': 7,
            r'session\.(user|logged)': 9,
            r'middleware.*auth': 10,
            r'@Authenticated': 10,
            r'@Secured': 10,
            r'@RolesAllowed': 10,
            r'Principal': 7
        }
    },
    'config_keys': {
        'simple': [
            r'auth', r'jwt', r'secret.*key', r'api.*key', r'token', r'firebase', 
            r'oauth', r'auth0', r'cognito', r'ALLOWED_HOSTS', r'CORS', 
            r'SESSION', r'COOKIE', r'KEY', r'AUTH_USER_MODEL', r'AUTHENTICATION_BACKENDS'
        ],
        'weighted': {
            r'JWT_SECRET': 10,
            r'SECRET_KEY': 9,
            r'API_KEY': 9,
            r'AUTH0_DOMAIN': 10,
            r'AUTH0_CLIENT': 10,
            r'OAUTH_': 10,
            r'COGNITO_': 10,
            r'AUTHENTICATION_BACKENDS': 10,
            r'AUTH_USER_MODEL': 10,
            r'SESSION_': 8,
            r'COOKIE_': 7,
            r'PASSWORD_HASHERS': 10,
            r'FIREBASE_AUTH': 10,
            r'CORS_': 7,
            r'ALLOWED_HOSTS': 7,
            r'SECURITY_': 8
        }
    },
    # Framework específicos
    'frameworks': {
        'express': [
            r'passport', r'jwt', r'express-session', r'jsonwebtoken', r'bcrypt',
            r'authenticate', r'isAuthenticated', r'auth\.', r'login', r'logout'
        ],
        'django': [
            r'django\.contrib\.auth', r'LoginView', r'LogoutView', r'UserCreationForm',
            r'AuthenticationForm', r'is_authenticated', r'login_required', r'permission_required',
            r'@login_required', r'@permission_required', r'user\.is_authenticated'
        ],
        'flask': [
            r'flask_login', r'flask_security', r'current_user', r'login_user',
            r'logout_user', r'@login_required', r'current_user\.is_authenticated'
        ],
        'spring': [
            r'spring\.security', r'@Secured', r'@RolesAllowed', r'Authentication',
            r'AuthenticationManager', r'SecurityContext', r'Principal'
        ],
        'react': [
            r'useAuth', r'AuthContext', r'AuthProvider', r'PrivateRoute',
            r'firebase\.auth', r'auth0-react', r'user\.isAuthenticated'
        ]
    },
    # Características específicas de autenticación
    'auth_features': {
        'jwt': [
            r'jwt', r'jsonwebtoken', r'encode', r'decode', r'verify', r'sign',
            r'Bearer', r'Authorization.*header'
        ],
        'oauth': [
            r'oauth', r'authorize', r'callback', r'client_id', r'client_secret',
            r'token_endpoint', r'authorization_endpoint', r'grant_type'
        ],
        'session': [
            r'session', r'cookie', r'store', r'persist', r'memcached', r'redis',
            r'session\.get', r'session\.set', r'withCredentials'
        ],
        'social_login': [
            r'facebook', r'google', r'twitter', r'github', r'linkedin', 
            r'social.*auth', r'social.*login', r'provider', r'strategy'
        ],
        'mfa': [
            r'mfa', r'2fa', r'two.*factor', r'multi.*factor', r'totp',
            r'one.*time.*password', r'verification.*code', r'authenticator'
        ]
    }
}

# Mapeo de frameworks a características
AUTH_FRAMEWORK_FEATURES = {
    'django': ['session', 'oauth'],
    'flask': ['session', 'oauth', 'jwt'],
    'express': ['jwt', 'session', 'oauth'],
    'spring': ['session', 'oauth', 'jwt'],
    'rails': ['session', 'oauth'],
    'react': ['jwt', 'oauth', 'social_login'],
    'angular': ['jwt', 'oauth', 'social_login'],
    'vue': ['jwt', 'oauth', 'social_login']
}

# Niveles de seguridad para cada tipo de autenticación
AUTH_SECURITY_LEVELS = {
    'plain_passwords': 'low',
    'hashed_passwords': 'medium',
    'hashed_with_salt': 'medium-high',
    'jwt_without_expiration': 'low',
    'jwt_with_expiration': 'medium',
    'jwt_with_refresh': 'medium-high',
    'oauth': 'high',
    'mfa': 'very-high'
}
