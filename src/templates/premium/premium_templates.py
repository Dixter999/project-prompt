#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plantillas premium para prompts de implementación.

Este módulo contiene plantillas avanzadas para generar guías
de implementación detalladas para diferentes tipos de funcionalidades.
"""

from typing import Dict, List, Any

# Plantilla para instrucción de implementación básica
IMPLEMENTATION_INSTRUCTION_TEMPLATE = """
# Guía de Implementación: {feature_name}

## Contexto del Proyecto
{project_context}

## Funcionalidad a Implementar
{feature_description}

## Directrices de Implementación
{implementation_guidelines}

## Consideraciones Técnicas
{technical_considerations}

## Referencias a Código Existente
{existing_code_references}
"""

# Descripciones de patrones de diseño para implementaciones
DESIGN_PATTERNS = {
    "mvc": {
        "name": "Modelo-Vista-Controlador (MVC)",
        "description": "Patrón que separa los datos, la lógica de negocio y la interfaz de usuario en componentes distintos.",
        "use_cases": ["aplicaciones web", "interfaces de usuario", "aplicaciones con múltiples vistas"],
        "example": """# Ejemplo de MVC en {language}:

## Modelo
```{language}
class {feature_name}Model:
    def __init__(self):
        self.data = {}
    
    def get_data(self):
        return self.data
    
    def set_data(self, key, value):
        self.data[key] = value
```

## Vista
```{language}
class {feature_name}View:
    def display(self, data):
        # Renderizar datos para el usuario
        pass
```

## Controlador
```{language}
class {feature_name}Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def update_model(self, key, value):
        self.model.set_data(key, value)
    
    def refresh_view(self):
        data = self.model.get_data()
        self.view.display(data)
```"""
    },
    "repository": {
        "name": "Patrón Repositorio",
        "description": "Patrón que separa la lógica de acceso a datos de la lógica de negocio.",
        "use_cases": ["acceso a bases de datos", "abstracción de fuentes de datos", "testing con mocks"],
        "example": """# Ejemplo de Repositorio en {language}:

## Interfaz del Repositorio
```{language}
class {feature_name}Repository:
    def get_by_id(self, id):
        pass
    
    def get_all(self):
        pass
    
    def add(self, item):
        pass
    
    def update(self, item):
        pass
    
    def delete(self, id):
        pass
```

## Implementación concreta
```{language}
class {feature_name}SqlRepository({feature_name}Repository):
    def __init__(self, db_connection):
        self.connection = db_connection
    
    def get_by_id(self, id):
        # Implementación SQL
        pass
```"""
    },
    "factory": {
        "name": "Patrón Fábrica",
        "description": "Patrón creacional que provee una interfaz para crear objetos sin especificar sus clases concretas.",
        "use_cases": ["creación de objetos complejos", "desacoplamiento", "configuración dinámica"],
        "example": """# Ejemplo de Fábrica en {language}:

```{language}
class {feature_name}Factory:
    @staticmethod
    def create(type):
        if type == "tipo1":
            return {feature_name}Tipo1()
        elif type == "tipo2":
            return {feature_name}Tipo2()
        else:
            raise ValueError(f"Tipo no soportado: {type}")
```"""
    },
    "strategy": {
        "name": "Patrón Estrategia",
        "description": "Patrón de comportamiento que permite seleccionar un algoritmo en tiempo de ejecución.",
        "use_cases": ["algoritmos intercambiables", "configuración en tiempo de ejecución", "eliminación de condicionales complejos"],
        "example": """# Ejemplo de Estrategia en {language}:

## Interfaz de estrategia
```{language}
class {feature_name}Strategy:
    def execute(self, data):
        pass
```

## Implementaciones concretas
```{language}
class {feature_name}StrategyA({feature_name}Strategy):
    def execute(self, data):
        # Implementación A
        pass

class {feature_name}StrategyB({feature_name}Strategy):
    def execute(self, data):
        # Implementación B
        pass
```

## Contexto
```{language}
class {feature_name}Context:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def execute_strategy(self, data):
        return self.strategy.execute(data)
```"""
    },
    "observer": {
        "name": "Patrón Observador",
        "description": "Patrón que define una dependencia uno a muchos entre objetos, notificando cambios.",
        "use_cases": ["eventos y notificaciones", "actualizaciones en tiempo real", "desacoplamiento entre componentes"],
        "example": """# Ejemplo de Observador en {language}:

## Sujeto (Observable)
```{language}
class {feature_name}Subject:
    def __init__(self):
        self.observers = []
        self.state = None
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def detach(self, observer):
        self.observers.remove(observer)
    
    def notify(self):
        for observer in self.observers:
            observer.update(self.state)
    
    def set_state(self, state):
        self.state = state
        self.notify()
```

## Observador
```{language}
class {feature_name}Observer:
    def update(self, state):
        # Reaccionar al cambio de estado
        pass
```"""
    },
}

# Patrones de código para diferentes tipos de operaciones
CODE_PATTERNS = {
    "api_endpoint": {
        "python_flask": """
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/{feature_path}', methods=['GET'])
def get_{feature_name_snake}():
    # Lógica de obtención de datos
    data = {{"result": "datos de {feature_name}"}}
    return jsonify(data)

@app.route('/{feature_path}', methods=['POST'])
def create_{feature_name_snake}():
    # Extraer datos de la solicitud
    request_data = request.get_json()
    
    # Procesar datos
    # ...
    
    # Responder
    return jsonify({{"status": "success", "message": "{feature_name} creado correctamente"}}), 201
""",
        "python_fastapi": """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class {feature_name_pascal}(BaseModel):
    name: str
    description: str
    # Otros campos necesarios

@app.get('/{feature_path}')
def get_{feature_name_snake}():
    # Lógica de obtención de datos
    return {{"result": "datos de {feature_name}"}}

@app.post('/{feature_path}')
def create_{feature_name_snake}({feature_variable}: {feature_name_pascal}):
    # Procesar datos
    # ...
    
    # Responder
    return {{"status": "success", "message": "{feature_name} creado correctamente"}}
""",
        "javascript_express": """
const express = require('express');
const router = express.Router();

// GET endpoint para {feature_name}
router.get('/{feature_path}', (req, res) => {
  // Lógica para obtener datos
  const data = {{ result: 'datos de {feature_name}' }};
  res.json(data);
});

// POST endpoint para {feature_name}
router.post('/{feature_path}', (req, res) => {
  // Extraer datos de la solicitud
  const {{ name, description }} = req.body;
  
  // Procesar datos
  // ...
  
  // Responder
  res.status(201).json({{ 
    status: 'success', 
    message: '{feature_name} creado correctamente' 
  }});
});

module.exports = router;
"""
    },
    "database_model": {
        "python_sqlalchemy": """
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class {feature_name_pascal}(Base):
    __tablename__ = '{feature_name_snake}s'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Otros campos según sea necesario
    
    # Relaciones
    # user_id = Column(Integer, ForeignKey('users.id'))
    # user = relationship("User", back_populates="{feature_name_snake}s")
    
    def __repr__(self):
        return f"<{feature_name_pascal}(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }}
""",
        "typescript_typeorm": """
import {{ 
  Entity, 
  Column, 
  PrimaryGeneratedColumn, 
  CreateDateColumn,
  UpdateDateColumn,
  // ManyToOne, 
  // OneToMany
}} from 'typeorm';

@Entity('{feature_name_snake}s')
export class {feature_name_pascal} {{
  @PrimaryGeneratedColumn()
  id: number;

  @Column({{ length: 100 }})
  name: string;

  @Column({{ length: 500, nullable: true }})
  description: string;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
  
  // Relaciones
  // @ManyToOne(() => User, user => user.{feature_name_camel}s)
  // user: User;
}}
"""
    },
    "service_layer": {
        "python": """
class {feature_name_pascal}Service:
    def __init__(self, repository):
        self.repository = repository
    
    def get_all(self):
        """Obtiene todos los {feature_name}s."""
        return self.repository.find_all()
    
    def get_by_id(self, id):
        """Obtiene un {feature_name} por su ID."""
        {feature_name} = self.repository.find_by_id(id)
        if not {feature_name}:
            raise ValueError(f"{feature_name_pascal} con id {{id}} no encontrado")
        return {feature_name}
    
    def create(self, data):
        """Crea un nuevo {feature_name}."""
        # Validación de datos
        if 'name' not in data or not data['name']:
            raise ValueError("El nombre es obligatorio")
            
        # Crear entidad
        new_{feature_name} = {feature_name_pascal}(
            name=data['name'],
            description=data.get('description', '')
            # Otros campos según sea necesario
        )
        
        # Guardar
        return self.repository.save(new_{feature_name})
    
    def update(self, id, data):
        """Actualiza un {feature_name} existente."""
        {feature_name} = self.get_by_id(id)  # Reutilizamos get_by_id con su validación
        
        # Actualizar campos
        if 'name' in data:
            {feature_name}.name = data['name']
        if 'description' in data:
            {feature_name}.description = data['description']
            
        # Guardar cambios
        return self.repository.save({feature_name})
    
    def delete(self, id):
        """Elimina un {feature_name}."""
        {feature_name} = self.get_by_id(id)  # Validar que existe
        self.repository.delete({feature_name})
""",
        "typescript": """
import {{ Injectable }} from '@angular/core';
// o cualquier otro framework que estés usando

@Injectable()
export class {feature_name_pascal}Service {{
  constructor(private repository: {feature_name_pascal}Repository) {{}}
  
  async getAll(): Promise<{feature_name_pascal}[]> {{
    // Obtiene todos los {feature_name}s
    return this.repository.findAll();
  }}
  
  async getById(id: number): Promise<{feature_name_pascal}> {{
    // Obtiene un {feature_name} por su ID
    const {feature_name_camel} = await this.repository.findById(id);
    
    if (!{feature_name_camel}) {{
      throw new Error(`{feature_name_pascal} con id ${{id}} no encontrado`);
    }}
    
    return {feature_name_camel};
  }}
  
  async create(data: {{name: string, description?: string}}): Promise<{feature_name_pascal}> {{
    // Validación
    if (!data.name) {{
      throw new Error('El nombre es obligatorio');
    }}
    
    // Crear entidad
    const new{feature_name_pascal} = new {feature_name_pascal}();
    new{feature_name_pascal}.name = data.name;
    new{feature_name_pascal}.description = data.description || '';
    
    // Guardar
    return this.repository.save(new{feature_name_pascal});
  }}
  
  async update(id: number, data: {{name?: string, description?: string}}): Promise<{feature_name_pascal}> {{
    // Obtener y validar
    const {feature_name_camel} = await this.getById(id);
    
    // Actualizar campos
    if (data.name) {{
      {feature_name_camel}.name = data.name;
    }}
    
    if (data.description !== undefined) {{
      {feature_name_camel}.description = data.description;
    }}
    
    // Guardar
    return this.repository.save({feature_name_camel});
  }}
  
  async delete(id: number): Promise<void> {{
    // Validar que existe
    await this.getById(id);
    
    // Eliminar
    await this.repository.delete(id);
  }}
}}
"""
    },
    "test_suite": {
        "python_pytest": """
import pytest
from {module_path} import {feature_name_pascal}

# Fixtures
@pytest.fixture
def {feature_name_snake}_fixture():
    return {feature_name_pascal}(
        name="Test {feature_name}",
        description="This is a test {feature_name}"
    )

# Tests
def test_{feature_name_snake}_creation({feature_name_snake}_fixture):
    {feature_name} = {feature_name_snake}_fixture
    assert {feature_name}.name == "Test {feature_name}"
    assert {feature_name}.description == "This is a test {feature_name}"

def test_{feature_name_snake}_service(mocker):
    # Mockear el repositorio
    mock_repo = mocker.Mock()
    mock_repo.find_by_id.return_value = {feature_name_pascal}(id=1, name="Test")
    
    # Crear servicio con el mock
    service = {feature_name_pascal}Service(mock_repo)
    
    # Probar get_by_id
    result = service.get_by_id(1)
    assert result.id == 1
    assert result.name == "Test"
    
    # Verificar que se llamó al repositorio
    mock_repo.find_by_id.assert_called_once_with(1)

def test_{feature_name_snake}_not_found(mocker):
    # Mockear el repositorio para que retorne None
    mock_repo = mocker.Mock()
    mock_repo.find_by_id.return_value = None
    
    # Crear servicio con el mock
    service = {feature_name_pascal}Service(mock_repo)
    
    # Debe lanzar ValueError cuando no se encuentra
    with pytest.raises(ValueError):
        service.get_by_id(999)
""",
        "typescript_jest": """
import {{ {feature_name_pascal} }} from '../{feature_path}/{feature_name_snake}';
import {{ {feature_name_pascal}Service }} from '../{feature_path}/{feature_name_snake}.service';

// Mocks
jest.mock('../{feature_path}/{feature_name_snake}.repository');

describe('{feature_name_pascal}', () => {{
  let service: {feature_name_pascal}Service;
  let repositoryMock: any;

  beforeEach(() => {{
    // Configurar mocks
    repositoryMock = {{
      findAll: jest.fn(),
      findById: jest.fn(),
      save: jest.fn(),
      delete: jest.fn()
    }};
    
    service = new {feature_name_pascal}Service(repositoryMock);
  }});

  it('should be defined', () => {{
    expect(service).toBeDefined();
  }});

  describe('getById', () => {{
    it('should return a {feature_name} when it exists', async () => {{
      // Preparar
      const mock{feature_name_pascal} = new {feature_name_pascal}();
      mock{feature_name_pascal}.id = 1;
      mock{feature_name_pascal}.name = 'Test';
      repositoryMock.findById.mockResolvedValue(mock{feature_name_pascal});
      
      // Ejecutar
      const result = await service.getById(1);
      
      // Verificar
      expect(result).toBe(mock{feature_name_pascal});
      expect(repositoryMock.findById).toHaveBeenCalledWith(1);
    }});

    it('should throw an error when {feature_name} does not exist', async () => {{
      // Preparar
      repositoryMock.findById.mockResolvedValue(null);
      
      // Verificar
      await expect(service.getById(999)).rejects.toThrow(
        Error(`{feature_name_pascal} con id 999 no encontrado`)
      );
    }});
  }});

  // Más tests para create, update, delete, etc.
}});
"""
    }
}

# Referencias a bibliotecas y herramientas comunes
LIBRARY_REFERENCES = {
    "python": {
        "web": ["Flask", "FastAPI", "Django", "Tornado", "Pyramid", "Bottle"],
        "data": ["Pandas", "NumPy", "SciPy", "Scikit-learn", "Matplotlib"],
        "database": ["SQLAlchemy", "Alembic", "PyMongo", "Peewee", "Tortoise ORM"],
        "testing": ["Pytest", "Unittest", "Nose", "Mock", "Hypothesis"],
        "async": ["Asyncio", "Trio", "Twisted", "AioHTTP"],
        "util": ["Requests", "BeautifulSoup", "Click", "Typer", "Rich"],
    },
    "javascript": {
        "web": ["Express", "Koa", "Hapi", "Fastify", "NestJS", "Next.js"],
        "frontend": ["React", "Vue", "Angular", "Svelte", "Preact"],
        "state": ["Redux", "MobX", "Zustand", "Recoil", "Vuex", "Pinia"],
        "database": ["Sequelize", "TypeORM", "Prisma", "Mongoose", "Knex"],
        "testing": ["Jest", "Mocha", "Chai", "Cypress", "Testing Library"],
        "util": ["Lodash", "Axios", "Day.js", "Zod", "Commander"],
    },
    "java": {
        "web": ["Spring Boot", "Micronaut", "Quarkus", "Jakarta EE", "Play"],
        "database": ["Hibernate", "JDBC", "JPA", "MyBatis", "jOOQ"],
        "testing": ["JUnit", "TestNG", "Mockito", "AssertJ", "Spock"],
        "util": ["Guava", "Apache Commons", "Lombok", "Jackson", "Gson"],
    },
    "go": {
        "web": ["Gin", "Echo", "Fiber", "Chi", "Buffalo"],
        "database": ["GORM", "Database/SQL", "SQLx", "PGX", "MongoDB driver"],
        "testing": ["Testing", "Testify", "Gomega", "Ginkgo"],
        "util": ["Cobra", "Viper", "Zap", "Logrus", "Wire"],
    }
}

# Consideraciones de arquitectura para diferentes tipos de aplicaciones
ARCHITECTURE_CONSIDERATIONS = {
    "web_api": """
## Consideraciones Arquitectónicas para API Web

### Capas recomendadas
1. **Capa de Presentación**: Controladores y endpoints REST
2. **Capa de Servicio**: Lógica de negocio
3. **Capa de Acceso a Datos**: Repositorios y modelos

### Patrones recomendados
- **Inyección de dependencias** para mejorar la testabilidad
- **Repositorio** para abstraer el acceso a datos
- **DTO (Data Transfer Objects)** para transferir datos entre capas

### Aspectos críticos
- Manejo de autenticación y autorización
- Validación de entradas
- Manejo de errores consistente
- Documentación de API (Swagger/OpenAPI)
- Estrategia de versionado de API

### Consideraciones de escalabilidad
- Arquitectura sin estado para facilitar escalado horizontal
- Uso de caché para recursos frecuentemente accedidos
- Optimización de consultas a base de datos
""",
    "frontend": """
## Consideraciones Arquitectónicas para Frontend

### Estructura recomendada
1. **Componentes de UI**: Elementos visuales reutilizables
2. **Contenedores**: Componentes con lógica y estado
3. **Servicios**: Comunicación con API y lógica compartida
4. **Estado**: Gestión centralizada del estado

### Patrones recomendados
- **Container/Presentational** para separar lógica y presentación
- **Flux/Redux** para manejo de estado predecible
- **HOC o Hooks** para lógica reutilizable

### Aspectos críticos
- Experiencia de usuario y tiempos de carga
- Manejo de estado y reactividad
- Estrategia de enrutamiento
- Optimización de rendimiento
- Compatibilidad con navegadores

### Consideraciones de mantenibilidad
- Separación de responsabilidades
- Pruebas unitarias para componentes
- Diseño adaptable y accesible
""",
    "microservice": """
## Consideraciones Arquitectónicas para Microservicios

### Estructura recomendada
1. **API Gateway**: Punto de entrada unificado
2. **Servicios independientes**: Funcionalidades específicas
3. **Bases de datos por servicio**: Persistencia independiente
4. **Bus de eventos**: Comunicación asíncrona

### Patrones recomendados
- **Circuit Breaker** para manejar fallos
- **CQRS** para separar lecturas y escrituras
- **Saga** para transacciones distribuidas

### Aspectos críticos
- Comunicación entre servicios
- Consistencia de datos
- Descubrimiento de servicios
- Monitoreo y observabilidad
- Despliegue y orquestación (Docker, Kubernetes)

### Consideraciones de escalabilidad
- Diseño para tolerancia a fallos
- Estrategias de backup y recuperación
- Balanceo de carga
- Escalado independiente de servicios
""",
}

# Plantillas de código para documentación y comentarios
CODE_DOCUMENTATION_TEMPLATES = {
    "python": {
        "class": '''"""
{class_name}: {short_description}

Esta clase implementa {functionality_description}.

Atributos:
    {attr1_name} ({attr1_type}): {attr1_description}
    {attr2_name} ({attr2_type}): {attr2_description}

Ejemplo:
    ```python
    {usage_example}
    ```
"""''',
        "function": '''"""
{function_description}

Args:
    {arg1_name} ({arg1_type}): {arg1_description}
    {arg2_name} ({arg2_type}): {arg2_description}

Returns:
    {return_type}: {return_description}

Raises:
    {exception_type}: {exception_description}

Ejemplo:
    ```python
    {usage_example}
    ```
"""''',
    },
    "typescript": {
        "class": """/**
 * {class_name} - {short_description}
 * 
 * Esta clase implementa {functionality_description}.
 *
 * @example
 * ```typescript
 * {usage_example}
 * ```
 */""",
        "function": """/**
 * {function_description}
 *
 * @param {arg1_name} - {arg1_description}
 * @param {arg2_name} - {arg2_description}
 * @returns {return_description}
 * @throws {exception_description}
 *
 * @example
 * ```typescript
 * {usage_example}
 * ```
 */""",
    },
}

# Lista de consideraciones de seguridad comunes
SECURITY_CONSIDERATIONS = [
    "Validación de todas las entradas del usuario para prevenir inyecciones",
    "Implementación de autenticación y autorización adecuadas",
    "Uso de HTTPS/SSL para proteger datos en tránsito",
    "Protección contra ataques CSRF en aplicaciones web",
    "Evitar exposición de información sensible en registros o mensajes de error",
    "Implementación de límites de tasa para prevenir ataques de fuerza bruta",
    "Almacenamiento seguro de secretos y credenciales",
    "Sanitización de datos de salida para prevenir XSS",
    "Configuración adecuada de encabezados de seguridad HTTP",
    "Actualización regular de dependencias para parchear vulnerabilidades",
]

# Lista de consideraciones de rendimiento comunes
PERFORMANCE_CONSIDERATIONS = [
    "Implementación de estrategias de caché donde sea apropiado",
    "Optimización de consultas a bases de datos y uso de índices",
    "Minimización de llamadas API y solicitudes de red",
    "Implementación de paginación para grandes conjuntos de datos",
    "Consideración de procesamiento asíncrono para tareas intensivas",
    "Optimización de carga y tamaño de recursos (imágenes, JS, CSS)",
    "Uso de técnicas de carga diferida (lazy loading)",
    "Implementación de estrategias de escalado horizontal",
    "Monitoreo del uso de memoria y posibles fugas",
    "Implementación de mecanismos de timeout para operaciones externas",
]

# Plantillas premium completas
PREMIUM_TEMPLATES = {
    "implementation_guide": """
# Guía de Implementación Detallada: {feature_name}

## Contexto del Proyecto

**Nombre del Proyecto:** {project_name}
**Tipo de Aplicación:** {project_type}
**Lenguajes Principales:** {main_languages}
**Frameworks Detectados:** {detected_frameworks}

## Análisis de la Funcionalidad

**Descripción:** {feature_description}

**Componentes Relacionados Detectados:**
{related_components}

**Dependencias Necesarias:**
{required_dependencies}

## Arquitectura Propuesta

{architecture_description}

## Plan de Implementación Paso a Paso

### 1. Preparación del Entorno

```{main_language}
{preparation_code}
```

### 2. Estructura de Datos

```{main_language}
{data_structure_code}
```

### 3. Implementación de la Lógica de Negocio

```{main_language}
{business_logic_code}
```

### 4. Interfaz de Usuario / API

```{main_language}
{interface_code}
```

### 5. Pruebas

```{main_language}
{test_code}
```

## Consideraciones Técnicas

### Patrones de Diseño Recomendados

{design_patterns}

### Optimización y Rendimiento

{performance_considerations}

### Seguridad

{security_considerations}

### Escalabilidad

{scalability_considerations}

## Referencias y Ejemplos

{references}

## Notas Adicionales

{additional_notes}
""",

    "integration_steps": """
# Guía de Integración: {feature_name} con {integrated_system}

## Resumen de la Integración

**Objetivo:** {integration_objective}
**Sistemas Involucrados:** {systems_involved}
**Tipo de Integración:** {integration_type}

## Diagrama de Flujo

```
{flow_diagram}
```

## Requisitos Previos

{prerequisites}

## Pasos de Integración

### 1. Configuración de Credenciales

```{main_language}
{credentials_code}
```

### 2. Implementación de Adaptadores

```{main_language}
{adapter_code}
```

### 3. Manejo de Eventos

```{main_language}
{event_handling_code}
```

### 4. Transformación de Datos

```{main_language}
{data_transformation_code}
```

### 5. Control de Errores

```{main_language}
{error_handling_code}
```

## Pruebas de Integración

```{main_language}
{integration_test_code}
```

## Consideraciones Operativas

{operational_considerations}

## Referencias de API

{api_references}
""",

    "refactoring_guide": """
# Guía de Refactorización: {feature_name}

## Análisis del Código Actual

**Problemas Identificados:**
{identified_problems}

**Métricas de Código:**
{code_metrics}

## Objetivos de la Refactorización

{refactoring_goals}

## Plan de Refactorización

### 1. Estructura del Código

**Antes:**
```{main_language}
{before_structure_code}
```

**Después:**
```{main_language}
{after_structure_code}
```

### 2. Patrones de Diseño

**Antes:**
```{main_language}
{before_patterns_code}
```

**Después:**
```{main_language}
{after_patterns_code}
```

### 3. Optimización de Rendimiento

**Antes:**
```{main_language}
{before_performance_code}
```

**Después:**
```{main_language}
{after_performance_code}
```

### 4. Mejora de Pruebas

```{main_language}
{improved_tests_code}
```

## Estrategia de Migración

{migration_strategy}

## Verificación de Resultados

{verification_steps}

## Referencias

{references}
"""
}