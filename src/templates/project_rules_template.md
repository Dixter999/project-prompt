# {{ project_name }} - Development Rules

## Project Overview
{{ project_description or "This project was analyzed by AI to generate development rules and guidelines." }}

**Generated on:** {{ timestamp }}  
**Analysis Confidence:** {{ confidence_score }}/1.0

{% if executive_summary %}
{{ executive_summary }}
{% endif %}

## Technology Constraints

### Mandatory Technologies
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'technology' and suggestion.suggested_rule.priority.value == 'mandatory' %}
- **{{ suggestion.context.get('technology_name', suggestion.suggested_rule.description) }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

### Recommended Technologies
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'technology' and suggestion.suggested_rule.priority.value == 'recommended' %}
- **{{ suggestion.context.get('technology_name', suggestion.suggested_rule.description) }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

### Prohibited Technologies
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'technology' and 'avoid' in suggestion.suggested_rule.content.lower() or 'not' in suggestion.suggested_rule.content.lower() or 'don\'t' in suggestion.suggested_rule.content.lower() %}
- {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

## Architecture Rules

### Service Structure
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'architecture' %}
- **{{ suggestion.suggested_rule.description }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

### File Organization
```
{% if project_structure %}
{{ project_structure }}
{% else %}
# Suggested project structure based on detected patterns:
{% for pattern in architectural_patterns %}
# {{ pattern }} pattern detected
{% endfor %}
src/
  ├── components/   # Reusable components
  ├── services/     # Business logic
  ├── utils/        # Helper functions
  ├── models/       # Data models
  ├── tests/        # Test files
  └── config/       # Configuration
{% endif %}
```

### Naming Conventions
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'naming' %}
- **{{ suggestion.suggested_rule.description }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

## Code Style Requirements

### Language Specific Rules
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'style' or suggestion.suggested_rule.category.value == 'formatting' %}
- **{{ suggestion.suggested_rule.description }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

### Error Handling
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'error_handling' %}
- **{{ suggestion.suggested_rule.description }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

## Testing Requirements

### Test Coverage and Quality
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'testing' %}
- **{{ suggestion.suggested_rule.description }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

### Testing Frameworks
{% for tech in technology_stack %}
{% if 'test' in tech.lower() or 'jest' in tech.lower() or 'pytest' in tech.lower() or 'junit' in tech.lower() %}
- **{{ tech }}**: Detected testing framework - follow established patterns
{% endif %}
{% endfor %}

## Security Requirements

{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'security' %}
### {{ suggestion.suggested_rule.description }}
{{ suggestion.suggested_rule.content }}

{% if suggestion.reasoning %}
**Reasoning:** {{ suggestion.reasoning }}
{% endif %}

{% endif %}
{% endfor %}

## Documentation Standards

### Code Documentation
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'documentation' %}
- **{{ suggestion.suggested_rule.description }}**: {{ suggestion.suggested_rule.content }}
{% endif %}
{% endfor %}

### Project Documentation
- README files required for major modules
- API documentation for all public interfaces
- Inline comments for complex business logic

## Performance Guidelines

{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.category.value == 'performance' %}
### {{ suggestion.suggested_rule.description }}
{{ suggestion.suggested_rule.content }}

{% if suggestion.examples %}
**Examples:**
{% for example in suggestion.examples %}
- {{ example }}
{% endfor %}
{% endif %}

{% endif %}
{% endfor %}

## AI Analysis Preferences

### Focus Areas
Based on the detected patterns in your project:
{% for pattern in current_practices %}
1. {{ pattern }}
{% endfor %}

### Detected Technologies
{% for tech in technology_stack %}
- **{{ tech }}**: {{ tech_details.get(tech, 'Detected in project') }}
{% endfor %}

### Suggestion Priorities
1. **High Priority (Mandatory)**: Rules that prevent bugs or security issues
2. **Medium Priority (Recommended)**: Best practices for maintainability  
3. **Low Priority (Optional)**: Nice-to-have improvements

{% if inconsistencies %}
### Detected Inconsistencies
{% for inconsistency in inconsistencies %}
- ⚠️ **{{ inconsistency.type }}**: {{ inconsistency.description }}
  - **Suggested Fix**: {{ inconsistency.suggested_fix }}
{% endfor %}
{% endif %}

## Custom Analysis Rules

### When analyzing this project:
{% for suggestion in suggestions %}
{% if suggestion.confidence > 0.8 and suggestion.suggested_rule.priority.value == 'mandatory' %}
1. {{ suggestion.suggested_rule.description }} (High confidence: {{ suggestion.confidence }})
{% endif %}
{% endfor %}

### When suggesting improvements:
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.priority.value == 'recommended' %}
1. {{ suggestion.reasoning }}
{% endif %}
{% endfor %}

## Implementation Roadmap

### Phase 1: Critical Rules (Week 1-2)
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.priority.value == 'mandatory' and suggestion.confidence > 0.8 %}
- [ ] **{{ suggestion.suggested_rule.description }}**
  - Implementation: {{ suggestion.suggested_rule.content }}
  - Confidence: {{ suggestion.confidence }}/1.0
{% endif %}
{% endfor %}

### Phase 2: Quality Improvements (Week 3-4)  
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.priority.value == 'recommended' and suggestion.confidence > 0.7 %}
- [ ] **{{ suggestion.suggested_rule.description }}**
  - Implementation: {{ suggestion.suggested_rule.content }}
  - Confidence: {{ suggestion.confidence }}/1.0
{% endif %}
{% endfor %}

### Phase 3: Optional Enhancements (Month 2)
{% for suggestion in suggestions %}
{% if suggestion.suggested_rule.priority.value == 'optional' or suggestion.confidence <= 0.7 %}
- [ ] **{{ suggestion.suggested_rule.description }}**
  - Implementation: {{ suggestion.suggested_rule.content }}
  - Confidence: {{ suggestion.confidence }}/1.0
{% endif %}
{% endfor %}

## Quality Metrics

### Current Project Health  
- **Code Consistency**: {{ metrics.consistency_score or 'N/A' }}/10
- **Documentation Coverage**: {{ metrics.documentation_score or 'N/A' }}/10  
- **Testing Maturity**: {{ metrics.testing_score or 'N/A' }}/10
- **Security Awareness**: {{ metrics.security_score or 'N/A' }}/10

### Expected Improvement with Rules
- **Code Consistency**: {{ metrics.projected_consistency or 'N/A' }}/10 (+{{ metrics.consistency_improvement or '0' }})
- **Documentation Coverage**: {{ metrics.projected_documentation or 'N/A' }}/10 (+{{ metrics.documentation_improvement or '0' }})
- **Testing Maturity**: {{ metrics.projected_testing or 'N/A' }}/10 (+{{ metrics.testing_improvement or '0' }})
- **Security Awareness**: {{ metrics.projected_security or 'N/A' }}/10 (+{{ metrics.security_improvement or '0' }})

---

## Analysis Details

**AI Analysis Method**: Automated pattern recognition and best practices comparison  
**Confidence Scoring**: Based on pattern strength and industry standards  
**Review Required**: Human validation recommended for all suggestions

*Generated by ProjectPrompt AI Rules Suggester - {{ timestamp }}*
