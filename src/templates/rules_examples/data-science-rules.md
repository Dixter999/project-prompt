# Data Science Project Rules

## Project Overview
This is a data science and machine learning project focused on reproducible research, clean data processing, and reliable model development.

## Technology Rules

### Mandatory
- Use Python 3.8+ for all data processing and analysis
- Use pandas for all data manipulation and analysis
- Use numpy for numerical computations
- Use Jupyter notebooks for exploration and prototyping [files: *.ipynb]
- Use scikit-learn for traditional machine learning models

### Recommended
- Use matplotlib/seaborn for data visualization
- Use plotly for interactive visualizations
- Use pytest for testing data processing functions
- Use poetry or pipenv for dependency management
- Use DVC (Data Version Control) for dataset versioning

### Optional
- Consider PyTorch or TensorFlow for deep learning projects
- Consider Apache Spark for big data processing
- Use MLflow for experiment tracking and model management

## Architecture Rules

### Mandatory
- Separate data ingestion, processing, analysis, and modeling code
- All data processing steps must be reproducible
- Use configuration files for all parameters and hyperparameters
- Implement proper data validation and quality checks
- All models must have evaluation metrics and validation

### Recommended
- Follow cookiecutter data science project structure
- Implement data pipelines with clear input/output specifications
- Use object-oriented design for complex data processing classes
- Implement proper logging for long-running processes

### Optional
- Consider implementing microservices for model serving
- Use containerization for model deployment

## Code Style Rules

### Mandatory
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Maximum function length: 50 lines
- All public functions must have docstrings with parameters and return types
- No magic numbers - use named constants

### Recommended
- Use meaningful variable names (avoid single letters except for iterators)
- Implement comprehensive docstrings following numpy/scipy format
- Use black for automatic code formatting
- Use descriptive notebook cell organization with markdown headers

### Optional
- Consider using dataclasses for structured data representation
- Implement code splitting for better modularity

## Testing Rules

### Mandatory
- Minimum 80% code coverage for all data processing functions
- All data transformation functions must have unit tests
- Implement data quality tests (schema validation, range checks)
- Mock all external data sources in tests
- Test model performance against baseline metrics

### Recommended
- Use property-based testing for data validation functions
- Implement integration tests for complete data pipelines
- Use great_expectations for data quality testing
- Test model predictions on known datasets

### Optional
- Consider using hypothesis for more robust testing
- Implement performance benchmarking tests

## Performance Rules

### Mandatory
- Use vectorized operations instead of loops where possible
- Profile code performance for data processing bottlenecks
- Implement efficient memory usage (chunking for large datasets)
- Use appropriate data types (e.g., category for categorical data)

### Recommended
- Use parallel processing for independent computations
- Implement caching for expensive computations
- Use appropriate data storage formats (parquet, HDF5)
- Monitor memory usage during data processing

### Optional
- Consider using Dask for out-of-core computations
- Implement GPU acceleration where appropriate

## Security Rules

### Mandatory
- Never commit data files or credentials to version control
- Use environment variables for sensitive configuration
- Implement proper data anonymization for sensitive datasets
- Secure API endpoints if exposing models as services

### Recommended
- Use encrypted storage for sensitive datasets
- Implement proper access controls for data and models
- Regular security audits for dependencies
- Use secure protocols for data transfer

### Optional
- Consider differential privacy for sensitive data analysis
- Implement federated learning for distributed sensitive data

## Documentation Rules

### Mandatory
- Document all data sources and their schemas
- Maintain a data dictionary for all variables
- Document model assumptions and limitations
- Include methodology documentation for analysis approaches
- README must include environment setup and execution instructions

### Recommended
- Use automated documentation generation tools (Sphinx)
- Document data collection and preprocessing decisions
- Include model interpretation and feature importance analysis
- Maintain experiment logs with results and conclusions

### Optional
- Create interactive dashboards for model results
- Implement automated report generation

## Deployment Rules

### Mandatory
- Use virtual environments for all projects
- Pin all dependency versions in requirements files
- Implement proper model versioning and tracking
- Use containerization for model deployment

### Recommended
- Implement CI/CD pipelines for model training and deployment
- Use model registries for production model management
- Implement model monitoring and drift detection
- Use infrastructure as code for reproducible environments

### Optional
- Consider using Kubernetes for scalable model serving
- Implement A/B testing frameworks for model comparison

## AI Analysis Preferences

### Focus Areas
1. Data quality and validation practices
2. Model performance and evaluation metrics
3. Code efficiency and pandas optimization
4. Reproducibility and experiment tracking
5. Statistical methodology and assumptions

### Suggestion Priorities
1. Data quality issues (missing data, outliers, inconsistencies)
2. Model validation and evaluation problems
3. Code performance and memory optimization
4. Reproducibility gaps
5. Statistical methodology improvements
6. Documentation completeness

## Custom Analysis Rules

### When analyzing this project:
1. Always check data loading and preprocessing steps for efficiency
2. Verify model evaluation includes appropriate metrics for the problem type
3. Ensure proper train/validation/test splits and cross-validation
4. Check for data leakage and overfitting issues
5. Validate statistical assumptions and methodology

### When suggesting improvements:
1. Prioritize data quality and validation improvements
2. Suggest pandas/numpy optimizations for performance
3. Recommend appropriate evaluation metrics and validation techniques
4. Focus on reproducibility and experiment tracking
5. Ensure suggestions follow data science best practices and statistical rigor