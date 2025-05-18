// ProjectPrompt Panel para VS Code
// Implementa el panel interactivo para visualizar y trabajar con ProjectPrompt

const vscode = require('vscode');
const path = require('path');

class ProjectPromptPanel {
    constructor(extensionUri, state) {
        this._extensionUri = extensionUri;
        this._state = state;
        this._panel = this._createWebviewPanel();
        this._setupPanel();
    }
    
    /**
     * Crea el panel de webview
     */
    _createWebviewPanel() {
        return vscode.window.createWebviewPanel(
            'projectPromptPanel',
            'ProjectPrompt',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(this._extensionUri, 'resources')
                ]
            }
        );
    }
    
    /**
     * Configura el panel y los manejadores de eventos
     */
    _setupPanel() {
        // Configurar contenido inicial
        this._panel.webview.html = this._getHtmlContent();
        
        // Manejar eventos de mensajes
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'analyze':
                        vscode.commands.executeCommand('projectprompt.analyzeProject');
                        return;
                    case 'generatePrompt':
                        vscode.commands.executeCommand('projectprompt.generatePrompt');
                        return;
                    case 'showDocs':
                        vscode.commands.executeCommand('projectprompt.showDocumentation');
                        return;
                    case 'openFile':
                        if (message.file) {
                            const fileUri = vscode.Uri.file(message.file);
                            vscode.commands.executeCommand('vscode.open', fileUri);
                        }
                        return;
                    case 'generateTests':
                        vscode.commands.executeCommand('projectprompt.generateTests');
                        return;
                    case 'checkCompleteness':
                        vscode.commands.executeCommand('projectprompt.checkFeatureCompleteness', message.feature);
                        return;
                    case 'upgradeToPremium':
                        vscode.commands.executeCommand('projectprompt.premium.showPlans');
                        return;
                    case 'sendToCopilot':
                        vscode.commands.executeCommand('projectprompt.sendToCopilot', message.content);
                        return;
                }
            },
            undefined,
            this._disposables
        );
        
        // Manejar cierre del panel
        this._panel.onDidDispose(
            () => {
                this._panel = undefined;
                
                // Notificar al estado que el panel se cerró
                if (this._state) {
                    this._state.panel = null;
                }
            },
            null,
            this._disposables
        );
    }
    
    /**
     * Genera el contenido HTML del panel
     */
    _getHtmlContent() {
        const webview = this._panel.webview;
        
        // Recursos locales
        const stylesUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'resources', 'styles.css')
        );
        
        const scriptUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'resources', 'main.js')
        );
        
        const logoUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'resources', 'logo.png')
        );
        
        // Información básica del proyecto
        const workspaceName = this._state.workspaceFolder ? 
            path.basename(this._state.workspaceFolder) : 'Sin proyecto';
        
        const hasAnalysis = this._state.lastAnalysis != null;
        
        // Generar HTML
        return `
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ProjectPrompt</title>
                <link href="${stylesUri}" rel="stylesheet">
            </head>
            <body>
                <header>
                    <div class="logo-container">
                        <img src="${logoUri}" alt="ProjectPrompt Logo" class="logo">
                        <h1>ProjectPrompt</h1>
                    </div>
                    <p class="version">v0.1.0</p>
                </header>
                
                <div class="project-info">
                    <h2>Proyecto: ${workspaceName}</h2>
                    <div class="status-bar">
                        <span class="status ${hasAnalysis ? 'ready' : 'pending'}">
                            ${hasAnalysis ? '✓ Analizado' : '⚠ Sin analizar'}
                        </span>
                    </div>
                </div>
                
                <div class="tabs">
                    <button class="tab-btn active" data-tab="dashboard">Dashboard</button>
                    <button class="tab-btn" data-tab="features">Características</button>
                    <button class="tab-btn" data-tab="prompts">Prompts</button>
                    <button class="tab-btn" data-tab="documentation">Documentación</button>
                    <button class="tab-btn" data-tab="copilot">GitHub Copilot</button>
                </div>
                
                <div class="tab-content" id="dashboard-tab" style="display: block;">
                    <div class="dashboard-container">
                        ${this._getDashboardContent()}
                    </div>
                </div>
                
                <div class="tab-content" id="features-tab">
                    <div class="features-container">
                        ${this._getFeaturesContent()}
                    </div>
                </div>
                
                <div class="tab-content" id="prompts-tab">
                    <div class="prompts-container">
                        ${this._getPromptsContent()}
                    </div>
                </div>
                
                <div class="tab-content" id="documentation-tab">
                    <div class="documentation-container">
                        ${this._getDocumentationContent()}
                    </div>
                </div>
                
                <div class="tab-content" id="copilot-tab">
                    <div class="copilot-container">
                        ${this._getCopilotContent()}
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="action-btn primary" id="analyze-btn">
                        Analizar Proyecto
                    </button>
                    <button class="action-btn" id="prompt-btn">
                        Generar Prompt
                    </button>
                    <button class="action-btn" id="docs-btn">
                        Ver Documentación
                    </button>
                </div>
                
                <script src="${scriptUri}"></script>
            </body>
            </html>
        `;
    }
    
    /**
     * Genera el contenido del panel de Dashboard
     */
    _getDashboardContent() {
        if (!this._state.lastAnalysis) {
            return `
                <div class="placeholder-container">
                    <p class="placeholder-text">
                        No hay datos de análisis disponibles. 
                        Haga clic en "Analizar Proyecto" para comenzar.
                    </p>
                </div>
            `;
        }
        
        const analysis = this._state.lastAnalysis;
        const stats = analysis.stats || {};
        const languages = analysis.languages || {};
        
        // Formatear estadísticas básicas
        const statsHtml = `
            <div class="stats-container">
                <div class="stat-card">
                    <span class="stat-value">${stats.total_files || 0}</span>
                    <span class="stat-label">Archivos</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${stats.total_dirs || 0}</span>
                    <span class="stat-label">Directorios</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${stats.analyzed_files || 0}</span>
                    <span class="stat-label">Archivos analizados</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${(stats.total_size_kb || 0).toLocaleString()} KB</span>
                    <span class="stat-label">Tamaño total</span>
                </div>
            </div>
        `;
        
        // Formatear lenguajes principales
        let languagesHtml = '<h3>Lenguajes Detectados</h3>';
        if (Object.keys(languages).length === 0) {
            languagesHtml += '<p>No se detectaron lenguajes.</p>';
        } else {
            languagesHtml += '<div class="languages-container">';
            
            // Ordenar lenguajes por porcentaje
            const sortedLanguages = Object.entries(languages)
                .sort((a, b) => b[1].percentage - a[1].percentage)
                .slice(0, 5); // Mostrar los 5 principales
                
            sortedLanguages.forEach(([lang, data]) => {
                languagesHtml += `
                    <div class="language-item">
                        <div class="language-name">${lang}</div>
                        <div class="language-bar">
                            <div class="language-progress" style="width: ${data.percentage}%"></div>
                        </div>
                        <div class="language-stats">
                            ${data.files} archivos · ${data.percentage.toFixed(1)}%
                        </div>
                    </div>
                `;
            });
            
            languagesHtml += '</div>';
        }
        
        // Mostrar características detectadas
        let featuresHtml = '<h3>Características Detectadas</h3>';
        const features = analysis.functionalities || [];
        
        if (features.length === 0) {
            featuresHtml += '<p>No se detectaron características específicas.</p>';
            featuresHtml += `
                <div class="premium-callout">
                    <h4>✨ Mejore la detección de características</h4>
                    <p>
                        Actualice a ProjectPrompt Premium para obtener detección avanzada de características
                        y análisis detallado de arquitectura.
                    </p>
                    <button class="premium-btn" id="upgrade-premium-btn">Ver planes premium</button>
                </div>
            `;
        } else {
            featuresHtml += '<ul class="features-list">';
            features.forEach(feature => {
                featuresHtml += `<li>${feature.name} (${feature.confidence}% confianza)</li>`;
            });
            featuresHtml += '</ul>';
        }
        
        return `
            <h2>Resumen del Proyecto</h2>
            ${statsHtml}
            ${languagesHtml}
            ${featuresHtml}
            
            <div class="actions-footer">
                <button class="action-btn" id="show-dashboard-btn">
                    Ver Dashboard Completo
                </button>
            </div>
        `;
    }
    
    /**
     * Genera el contenido del panel de Características
     */
    _getFeaturesContent() {
        if (!this._state.lastAnalysis) {
            return `
                <div class="placeholder-container">
                    <p class="placeholder-text">
                        No hay datos de análisis disponibles.
                        Primero debe analizar el proyecto.
                    </p>
                </div>
            `;
        }
        
        const features = this._state.lastAnalysis.functionalities || [];
        
        if (features.length === 0) {
            return `
                <div class="placeholder-container">
                    <p class="placeholder-text">
                        No se detectaron características específicas en el proyecto.
                    </p>
                </div>
                
                <div class="premium-callout">
                    <h3>✨ Mejore la detección de características</h3>
                    <p>
                        Actualice a ProjectPrompt Premium para obtener detección avanzada de características
                        y análisis detallado de arquitectura.
                    </p>
                    <button class="premium-btn" id="upgrade-premium-btn">Ver planes premium</button>
                </div>
            `;
        }
        
        let featuresHtml = '';
        features.forEach(feature => {
            featuresHtml += `
                <div class="feature-card">
                    <h3>${feature.name}</h3>
                    <div class="feature-meta">
                        <span class="confidence">Confianza: ${feature.confidence}%</span>
                        ${feature.status ? `<span class="status">${feature.status}</span>` : ''}
                    </div>
                    
                    ${feature.description ? `<p>${feature.description}</p>` : ''}
                    
                    ${feature.files && feature.files.length > 0 ? `
                        <h4>Archivos relacionados:</h4>
                        <ul class="files-list">
                            ${feature.files.map(file => `
                                <li>
                                    <a href="#" class="file-link" data-path="${file}">${file}</a>
                                </li>
                            `).join('')}
                        </ul>
                    ` : ''}
                    
                    <div class="feature-actions">
                        <button class="feature-btn check-btn" data-feature="${feature.name}">
                            Verificar completitud
                        </button>
                        <button class="feature-btn test-btn" data-feature="${feature.name}">
                            Generar tests
                        </button>
                    </div>
                </div>
            `;
        });
        
        return featuresHtml;
    }
    
    /**
     * Genera el contenido del panel de Prompts
     */
    _getPromptsContent() {
        return `
            <div class="prompts-intro">
                <h2>Generación de Prompts Contextuales</h2>
                <p>
                    ProjectPrompt puede generar prompts de alta calidad con contexto
                    específico de su proyecto para utilizar con modelos de lenguaje como
                    GitHub Copilot, Claude o ChatGPT.
                </p>
            </div>
            
            <div class="prompts-options">
                <div class="prompt-option">
                    <h3>📁 Prompt para archivo</h3>
                    <p>Genera un prompt contextual para un archivo específico del proyecto.</p>
                    <button class="prompt-btn" id="file-prompt-btn">Seleccionar archivo</button>
                </div>
                
                <div class="prompt-option">
                    <h3>✨ Prompt para funcionalidad</h3>
                    <p>Genera un prompt orientado a una funcionalidad específica del proyecto.</p>
                    <button class="prompt-btn" id="feature-prompt-btn">Seleccionar funcionalidad</button>
                </div>
                
                <div class="prompt-option">
                    <h3>📝 Prompt para selección</h3>
                    <p>Genera un prompt a partir de texto seleccionado en el editor.</p>
                    <button class="prompt-btn" id="selection-prompt-btn">Desde selección</button>
                </div>
                
                <div class="prompt-option premium">
                    <h3>🔍 Prompt de implementación</h3>
                    <p>Genera un prompt detallado para implementar una característica (premium).</p>
                    <button class="prompt-btn premium-btn" id="implementation-prompt-btn">
                        Generar prompt de implementación
                    </button>
                </div>
            </div>
            
            <div class="prompts-history">
                <h3>Historial de Prompts</h3>
                <p class="placeholder-text">Aquí aparecerán los prompts generados recientemente.</p>
            </div>
        `;
    }
    
    /**
     * Genera el contenido del panel de Documentación
     */
    _getDocumentationContent() {
        return `
            <div class="documentation-intro">
                <h2>Documentación del Proyecto</h2>
                <p>
                    ProjectPrompt puede generar y mantener documentación estructurada
                    sobre su proyecto para facilitar la comprensión y mantenimiento.
                </p>
            </div>
            
            <div class="documentation-options">
                <div class="doc-option">
                    <h3>📄 Ver documentación existente</h3>
                    <p>Explora la documentación ya generada para este proyecto.</p>
                    <button class="doc-btn" id="view-docs-btn">Ver documentación</button>
                </div>
                
                <div class="doc-option">
                    <h3>🔄 Generar/actualizar documentación</h3>
                    <p>Genera o actualiza la documentación del proyecto.</p>
                    <button class="doc-btn" id="generate-docs-btn">Generar documentación</button>
                </div>
                
                <div class="doc-option premium">
                    <h3>🔍 Documentación detallada (Premium)</h3>
                    <p>Genera documentación avanzada con diagramas, relaciones y más.</p>
                    <button class="doc-btn premium-btn" id="premium-docs-btn">
                        Documentación premium
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Genera el contenido del panel de integración con GitHub Copilot
     */
    _getCopilotContent() {
        const copilotAvailable = this._state.copilotAvailable === true;
        
        return `
            <div class="copilot-intro">
                <h2>Integración con GitHub Copilot</h2>
                <p>
                    ProjectPrompt puede generar prompts optimizados para GitHub Copilot
                    basados en el análisis de su proyecto.
                </p>
                
                <div class="copilot-status">
                    <span class="status ${copilotAvailable ? 'ready' : 'pending'}">
                        ${copilotAvailable 
                            ? '✓ GitHub Copilot detectado' 
                            : '⚠ GitHub Copilot no detectado'}
                    </span>
                    ${!copilotAvailable ? `
                        <p class="status-message">
                            Para utilizar esta función, instale y configure la extensión de GitHub Copilot
                            desde el marketplace de VS Code.
                        </p>
                    ` : ''}
                </div>
            </div>
            
            <div class="copilot-options">
                <div class="copilot-option">
                    <h3>🤖 Enviar prompt a Copilot</h3>
                    <p>Envía un prompt contextual generado por ProjectPrompt a GitHub Copilot.</p>
                    <button class="copilot-btn ${!copilotAvailable ? 'disabled' : ''}" 
                            id="send-to-copilot-btn" ${!copilotAvailable ? 'disabled' : ''}>
                        Enviar a Copilot
                    </button>
                </div>
                
                <div class="copilot-option">
                    <h3>✨ Prompt de implementación</h3>
                    <p>Genera un prompt de implementación y envíalo a GitHub Copilot.</p>
                    <button class="copilot-btn ${!copilotAvailable ? 'disabled' : ''}" 
                            id="implementation-copilot-btn" ${!copilotAvailable ? 'disabled' : ''}>
                        Implementación con Copilot
                    </button>
                </div>
                
                <div class="copilot-option">
                    <h3>🧪 Prompt para tests</h3>
                    <p>Genera tests automáticamente usando GitHub Copilot.</p>
                    <button class="copilot-btn ${!copilotAvailable ? 'disabled' : ''}" 
                            id="test-copilot-btn" ${!copilotAvailable ? 'disabled' : ''}>
                        Generar tests con Copilot
                    </button>
                </div>
            </div>
            
            <div class="copilot-tips">
                <h3>Consejos para usar Copilot con ProjectPrompt</h3>
                <ul>
                    <li>Use el comando "ProjectPrompt: Enviar a GitHub Copilot" en el menú contextual del editor con texto seleccionado.</li>
                    <li>Los prompts generados por ProjectPrompt están optimizados para Copilot con el contexto específico de su proyecto.</li>
                    <li>Combine el análisis de proyecto con Copilot para obtener sugerencias de código más precisas.</li>
                </ul>
            </div>
        `;
    }
    
    /**
     * Actualiza el contenido del panel con nueva información
     */
    updateContent(section, data) {
        if (!this._panel) return;
        
        // Enviar mensaje al webview para actualizar contenido
        this._panel.webview.postMessage({
            command: 'update',
            section: section,
            data: data
        });
    }
    
    /**
     * Muestra el panel o lo trae al frente si ya está visible
     */
    reveal() {
        if (this._panel) {
            this._panel.reveal(vscode.ViewColumn.One);
        }
    }
    
    /**
     * Dispone de los recursos del panel
     */
    dispose() {
        if (this._panel) {
            this._panel.dispose();
        }
        
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}

module.exports = ProjectPromptPanel;
