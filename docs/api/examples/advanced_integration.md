# Ejemplos avanzados de integración de la API

Este documento muestra ejemplos avanzados de integración de la API de ProjectPrompt en diferentes escenarios y casos de uso.

## Integración en flujos de trabajo de desarrollo

### Integración con Git hooks

```python
#!/usr/bin/env python3
# pre-commit hook para analizar cambios y sugerir mejoras

import sys
import os
from project_prompt import ProjectAnalyzer, PromptGenerator, AIModelIntegrator

def main():
    # Obtener archivos modificados
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    modified_files = result.stdout.strip().split("\n")

    # Filtrar solo archivos Python
    python_files = [f for f in modified_files if f.endswith(".py")]
    if not python_files:
        print("No hay archivos Python modificados.")
        sys.exit(0)

    # Analizar los archivos modificados
    analyzer = ProjectAnalyzer(".")
    analysis = analyzer.analyze_files(python_files)
    
    # Generar prompt para revisión de código
    generator = PromptGenerator()
    prompt = generator.generate(
        project_data=analysis,
        task="Revisar cambios para identificar posibles mejoras o problemas",
        context_level="high"
    )
    
    # Consultar a la IA
    model = AIModelIntegrator.create(
        provider="openai",
        model_name="gpt-4"
    )
    response = model.complete(prompt=prompt)
    
    # Mostrar sugerencias
    print("\n==== SUGERENCIAS DE MEJORA ====")
    print(response.content)
    
    # Preguntar si continuar con el commit
    user_input = input("\n¿Continuar con el commit? (s/n): ").strip().lower()
    if user_input != "s":
        print("Commit abortado. Revisa las sugerencias.")
        sys.exit(1)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
```

Para instalar este hook:

```bash
cp script.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Integración con sistemas CI/CD

### Ejemplo para GitHub Actions

```yaml
# .github/workflows/prompt-quality.yml
name: Code Quality Check

on:
  pull_request:
    branches: [ main, develop ]
    
jobs:
  analyze-code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Obtener todo el historial
          
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install project-prompt
          
      - name: Analyze changes
        id: analysis
        run: |
          # Obtener archivos cambiados
          CHANGED_FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.sha }})
          
          # Script Python para análisis
          python - << 'EOF'
import os
import json
from project_prompt import ProjectAnalyzer, PromptGenerator, AIModelIntegrator

# Configurar API key desde secrets
os.environ["OPENAI_API_KEY"] = "${{ secrets.OPENAI_API_KEY }}"

# Analizar proyecto
analyzer = ProjectAnalyzer(".")
analysis = analyzer.analyze()

# Generar prompt para revisión de código
generator = PromptGenerator()
prompt = generator.generate(
    project_data=analysis,
    task="Revisar cambios de PR para detectar problemas de calidad y seguridad",
    additional_context="Este es un pull request de GitHub. Solo enfócate en los archivos modificados."
)

# Consultar a la IA
model = AIModelIntegrator.create(
    provider="openai",
    model_name="gpt-4"
)
response = model.complete(prompt=prompt)

# Guardar el resultado
with open("analysis_result.md", "w") as f:
    f.write("# Análisis de calidad de código\n\n")
    f.write(response.content)

# Exportar métricas
metrics = analyzer.get_metrics()
with open("metrics.json", "w") as f:
    json.dump(metrics, f)
EOF
          
      - name: Upload analysis results
        uses: actions/upload-artifact@v2
        with:
          name: code-analysis
          path: |
            analysis_result.md
            metrics.json
            
      - name: Add comment to PR
        uses: actions/github-script@v5
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const analysis = fs.readFileSync('analysis_result.md', 'utf8');
            const issueNumber = context.issue.number;
            github.rest.issues.createComment({
              issue_number: issueNumber,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: analysis
            });
```

## Integración con editor de código

### Extensión para VSCode (ejemplo simplificado)

```javascript
// extension.js
const vscode = require('vscode');
const { spawn } = require('child_process');

function activate(context) {
  console.log('ProjectPrompt extension is now active');

  // Registrar comando para análisis de proyecto
  let analyzeCommand = vscode.commands.registerCommand('projectPrompt.analyzeProject', async function () {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
      vscode.window.showErrorMessage('Abre un proyecto para analizarlo');
      return;
    }

    const projectPath = workspaceFolders[0].uri.fsPath;
    const progressOptions = {
      location: vscode.ProgressLocation.Notification,
      title: "Analizando proyecto...",
      cancellable: true
    };

    await vscode.window.withProgress(progressOptions, async (progress, token) => {
      return new Promise((resolve, reject) => {
        // Ejecutar script Python que usa la API de ProjectPrompt
        const pythonProcess = spawn('python', ['-c', `
import json
from project_prompt import ProjectAnalyzer

analyzer = ProjectAnalyzer("${projectPath}")
analysis = analyzer.analyze()

# Convertir a JSON para el proceso JS
print(json.dumps({
    "file_count": analysis.file_count,
    "language_stats": analysis.language_stats,
    "detected_frameworks": analysis.detected_technologies,
    "complexity_score": analysis.get_complexity_score()
}))
        `]);

        let result = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
          result += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
          error += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            try {
              const analysisData = JSON.parse(result);
              
              // Crear y mostrar panel con resultados
              const panel = vscode.window.createWebviewPanel(
                'projectAnalysis',
                'Análisis de Proyecto',
                vscode.ViewColumn.One,
                {}
              );
              
              panel.webview.html = getWebviewContent(analysisData);
              resolve();
            } catch (e) {
              vscode.window.showErrorMessage(`Error al procesar resultados: ${e.message}`);
              reject(e);
            }
          } else {
            vscode.window.showErrorMessage(`Error en el análisis: ${error}`);
            reject(new Error(error));
          }
        });
      });
    });
  });

  context.subscriptions.push(analyzeCommand);
}

function getWebviewContent(analysis) {
  return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Análisis de Proyecto</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .card { background: #f3f3f3; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
        .stats { display: flex; flex-wrap: wrap; gap: 10px; }
        .stat-item { background: #e0e0e0; padding: 8px; border-radius: 4px; }
      </style>
    </head>
    <body>
      <h1>Análisis de Proyecto</h1>
      
      <div class="card">
        <h2>Estadísticas Generales</h2>
        <p>Archivos totales: ${analysis.file_count}</p>
        <p>Puntuación de complejidad: ${analysis.complexity_score}/10</p>
      </div>
      
      <div class="card">
        <h2>Lenguajes Detectados</h2>
        <div class="stats">
          ${Object.entries(analysis.language_stats).map(([lang, count]) => 
            `<div class="stat-item">${lang}: ${count} archivos</div>`
          ).join('')}
        </div>
      </div>
      
      <div class="card">
        <h2>Frameworks y Tecnologías</h2>
        <div class="stats">
          ${analysis.detected_frameworks.map(framework => 
            `<div class="stat-item">${framework}</div>`
          ).join('')}
        </div>
      </div>
    </body>
    </html>`;
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
```

## Integración con aplicación web

### Ejemplo de API REST con Flask

```python
from flask import Flask, request, jsonify
from project_prompt import ProjectAnalyzer, PromptGenerator
import tempfile
import os
import shutil
import zipfile
import uuid

app = Flask(__name__)

# Directorio para almacenar proyectos subidos temporalmente
UPLOAD_DIR = tempfile.mkdtemp()

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    if 'project' not in request.files:
        return jsonify({"error": "No project file provided"}), 400
    
    file = request.files['project']
    
    # Crear directorio temporal único para este análisis
    analysis_id = str(uuid.uuid4())
    project_dir = os.path.join(UPLOAD_DIR, analysis_id)
    os.makedirs(project_dir)
    
    try:
        # Guardar y extraer el archivo zip
        zip_path = os.path.join(project_dir, "project.zip")
        file.save(zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(project_dir)
        
        # Analizar el proyecto
        analyzer = ProjectAnalyzer(project_dir)
        analysis = analyzer.analyze()
        
        # Preparar respuesta
        response = {
            "analysis_id": analysis_id,
            "file_count": analysis.file_count,
            "language_stats": analysis.language_stats,
            "technologies": analysis.detected_technologies,
            "complexity": analysis.get_complexity_score(),
            "structure_summary": analysis.get_structure_summary()
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Limpiar en caso de error
        shutil.rmtree(project_dir, ignore_errors=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_prompt():
    data = request.json
    if not data or 'analysis_id' not in data or 'task' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    analysis_id = data['analysis_id']
    task = data['task']
    model = data.get('model', 'gpt-4')
    
    project_dir = os.path.join(UPLOAD_DIR, analysis_id)
    if not os.path.exists(project_dir):
        return jsonify({"error": "Invalid analysis ID"}), 404
    
    try:
        # Reutilizar análisis previo
        analyzer = ProjectAnalyzer(project_dir)
        analysis = analyzer.analyze()
        
        # Generar prompt
        generator = PromptGenerator()
        prompt = generator.generate(
            project_data=analysis,
            task=task,
            model=model
        )
        
        return jsonify({"prompt": prompt})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Tarea periódica de limpieza (idealmente usando un scheduler)
@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_analyses():
    # Implementación real debería verificar autorización
    import time
    from datetime import datetime, timedelta
    
    cutoff_time = time.time() - 86400  # 24 horas
    
    deleted = 0
    for analysis_id in os.listdir(UPLOAD_DIR):
        dir_path = os.path.join(UPLOAD_DIR, analysis_id)
        if os.path.isdir(dir_path):
            # Verificar tiempo de creación
            creation_time = os.path.getctime(dir_path)
            if creation_time < cutoff_time:
                shutil.rmtree(dir_path, ignore_errors=True)
                deleted += 1
    
    return jsonify({"message": f"Deleted {deleted} old analyses"})

if __name__ == '__main__':
    app.run(debug=True)
```
