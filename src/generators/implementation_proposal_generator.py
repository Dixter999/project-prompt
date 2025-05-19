#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de propuestas de implementación para funcionalidades detectadas.
"""
import os
from typing import Dict, Any, List, Optional

from src.utils.logger import get_logger
from src.templates.proposals import generic as generic_proposal

# Importamos plantillas especializadas
try:
    from src.templates.proposals import auth_proposal
except ImportError:
    auth_proposal = None

try:
    from src.templates.proposals import database_proposal
except ImportError:
    database_proposal = None

logger = get_logger()

class ImplementationProposalGenerator:
    """
    Genera propuestas detalladas para implementar o mejorar funcionalidades.
    """
    def __init__(self):
        # Plantilla genérica siempre disponible
        self.templates = {
            'generic': generic_proposal.PROPOSAL_TEMPLATE,
        }
        
        # Cargar plantillas especializadas si están disponibles
        if auth_proposal:
            self.templates['auth'] = auth_proposal.AUTH_PROPOSAL_TEMPLATE
            
        if database_proposal:
            self.templates['database'] = database_proposal.DATABASE_PROPOSAL_TEMPLATE
            
        # Mapeo de palabras clave para detectar tipo de funcionalidad
        self.functionality_mappings = {
            'auth': ['autenticación', 'auth', 'login', 'registro', 'usuario'],
            'database': ['base de datos', 'db', 'datos', 'almacenamiento', 'sql', 'nosql'],
        }

    def select_template_for_functionality(self, functionality: str) -> str:
        """
        Selecciona la plantilla más adecuada para una funcionalidad.
        
        Args:
            functionality: Nombre de la funcionalidad
            
        Returns:
            Nombre de la plantilla a utilizar
        """
        functionality_lower = functionality.lower()
        
        # Buscar coincidencias con palabras clave
        for template_name, keywords in self.functionality_mappings.items():
            # Si alguna palabra clave está en el nombre de la funcionalidad
            # y tenemos esa plantilla, la usamos
            if any(keyword in functionality_lower for keyword in keywords) and template_name in self.templates:
                logger.debug(f"Seleccionada plantilla especializada '{template_name}' para '{functionality}'")
                return template_name
                
        # Si no hay coincidencias, usar plantilla genérica
        logger.debug(f"Usando plantilla genérica para '{functionality}'")
        return 'generic'
    
    def generate_proposal(self, functionality: str, context: Dict[str, Any]) -> str:
        """
        Genera una propuesta de implementación para una funcionalidad.
        
        Args:
            functionality: Nombre de la funcionalidad
            context: Contexto relevante (archivos, dependencias, requisitos, etc.)
            
        Returns:
            Propuesta en formato Markdown
        """
        # Seleccionar plantilla apropiada
        template_name = self.select_template_for_functionality(functionality)
        template = self.templates.get(template_name, self.templates['generic'])

        # Preparar contexto con valores por defecto para plantillas específicas
        if template_name == 'auth' and 'auth_mechanism' not in context:
            context['auth_mechanism'] = 'Autenticación basada en tokens JWT'
            context['security_elements'] = ''
            
        if template_name == 'database':
            if 'db_type' not in context:
                context['db_type'] = 'Relacional (SQL)'
            if 'data_structure' not in context:
                context['data_structure'] = 'Por definir en base a los requisitos'
            if 'schema_section' not in context:
                context['schema_section'] = 'Por definir'
            if 'operations_section' not in context:
                context['operations_section'] = ''
        
        # Generar propuesta usando la plantilla seleccionada
        try:
            return template.format(functionality=functionality, **context)
        except KeyError as e:
            logger.error(f"Error al generar propuesta: Falta la clave {e} en el contexto")
            # Intentar con plantilla genérica como fallback
            if template_name != 'generic':
                logger.info("Intentando con plantilla genérica como alternativa")
                template = self.templates['generic']
                return template.format(functionality=functionality, **context)
            raise


def get_implementation_proposal_generator() -> ImplementationProposalGenerator:
    return ImplementationProposalGenerator()
