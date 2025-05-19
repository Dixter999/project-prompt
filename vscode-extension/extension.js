// ProjectPrompt VS Code Extension
// Integración del asistente inteligente para proyectos usando IA

const vscode = require('vscode');
const path = require('path');
const fs = require('fs-extra');
const os = require('os');
const { execSync } = require('child_process');
const ProjectPromptPanel = require('./src/panel');
const FeatureProvider = require('./src/providers/featureProvider');
const DocumentationProvider = require('./src/providers/documentationProvider');
const PromptProvider = require('./src/providers/promptProvider');
const PremiumProvider = require('./src/providers/premiumProvider');
const CopilotIntegration = require('./src/integrations/copilot');

/**
 * @param {vscode.ExtensionContext} context
 */
async function activate(context) {
    console.log('ProjectPrompt se está activando...');
    
    // Inicializar estado
    const state = {
        initialized: false,
        pythonPath: vscode.workspace.getConfiguration('projectprompt').get('pythonPath'),
        workspaceFolder: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
        panel: null,
        providers: {},
        lastAnalysis: null
    };
    
    // Verificar requisitos
    const pythonInstalled = checkPythonInstallation(state.pythonPath);
    if (!pythonInstalled) {
        vscode.window.showErrorMessage('No se encontró Python. Por favor, instala Python 3.7+ para usar ProjectPrompt.');
    }
    
    // Verificar si ProjectPrompt está instalado
    const installed = await checkProjectPromptInstallation();
    if (!installed) {
        const action = await vscode.window.showWarningMessage(
            'ProjectPrompt no está instalado en su entorno de Python. ¿Desea instalarlo?',
            'Instalar', 'Cancelar'
        );
        
        if (action === 'Instalar') {
            await installProjectPrompt();
        }
    } else {
        state.initialized = true;
    }
    
    // Inicializar integración con GitHub Copilot
    state.copilotAvailable = await CopilotIntegration.initialize(state);
    
    // Proveedores de datos para las vistas
    state.providers = {
        features: new FeatureProvider(state),
        documentation: new DocumentationProvider(state),
        prompts: new PromptProvider(state),
        premium: new PremiumProvider(state)
    };
    
    // Registro de proveedores de vistas
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('projectprompt.featuresView', state.providers.features),
        vscode.window.registerTreeDataProvider('projectprompt.documentationView', state.providers.documentation),
        vscode.window.registerTreeDataProvider('projectprompt.promptsView', state.providers.prompts),
        vscode.window.registerTreeDataProvider('projectprompt.premiumView', state.providers.premium)
    );
    
    // Comando: Mostrar panel principal
    const showPanelCommand = vscode.commands.registerCommand('projectprompt.showPanel', async () => {
        if (!state.initialized) {
            vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
            return;
        }
        
        if (!state.panel) {
            state.panel = new ProjectPromptPanel(context.extensionUri, state);
        }
        
        state.panel.reveal();
    });
    
    // Comando: Analizar proyecto
    const analyzeProjectCommand = vscode.commands.registerCommand('projectprompt.analyzeProject', async (resource) => {
        if (!state.initialized) {
            vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
            return;
        }
        
        const projectPath = resource?.fsPath || state.workspaceFolder;
        if (!projectPath) {
            vscode.window.showErrorMessage('No hay ninguna carpeta de proyecto abierta.');
            return;
        }
        
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "ProjectPrompt: Analizando proyecto...",
                cancellable: true
            }, async (progress) => {
                progress.report({ increment: 10, message: "Iniciando análisis..." });
                
                const result = await runProjectPromptCommand(['analyze', projectPath]);
                progress.report({ increment: 90, message: "Análisis completado" });
                
                if (result.success) {
                    state.lastAnalysis = result.data;
                    
                    // Actualizar vistas
                    state.providers.features.refresh();
                    state.providers.documentation.refresh();
                    
                    vscode.window.showInformationMessage('Análisis de proyecto completado.');
                    
                    // Mostrar resumen
                    if (!state.panel) {
                        state.panel = new ProjectPromptPanel(context.extensionUri, state);
                    }
                    state.panel.reveal();
                } else {
                    vscode.window.showErrorMessage(`Error al analizar el proyecto: ${result.error}`);
                }
                
                return result.success;
            });
        } catch (err) {
            vscode.window.showErrorMessage(`Error en el análisis: ${err.message}`);
        }
    });
    
    // Comando: Generar prompt contextual
    const generatePromptCommand = vscode.commands.registerCommand('projectprompt.generatePrompt', async (resource) => {
        if (!state.initialized) {
            vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
            return;
        }
        
        // Determinar si es archivo o selección de texto
        let target = resource?.fsPath;
        let selectedText = '';
        
        if (!target) {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                target = editor.document.uri.fsPath;
                const selection = editor.selection;
                if (!selection.isEmpty) {
                    selectedText = editor.document.getText(selection);
                }
            }
        }
        
        if (!target) {
            vscode.window.showErrorMessage('No se ha seleccionado ningún archivo o texto.');
            return;
        }
        
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "ProjectPrompt: Generando prompt...",
                cancellable: true
            }, async (progress) => {
                progress.report({ increment: 20, message: "Analizando contexto..." });
                
                const args = ['generate_prompts', target];
                if (selectedText) {
                    // Guardar la selección en un archivo temporal
                    const tmpFile = path.join(os.tmpdir(), 'projectprompt_selection.txt');
                    fs.writeFileSync(tmpFile, selectedText, 'utf8');
                    args.push('--selection', tmpFile);
                }
                
                const result = await runProjectPromptCommand(args);
                progress.report({ increment: 80, message: "Prompt generado" });
                
                if (result.success) {
                    // Crear un nuevo documento con el prompt
                    const document = await vscode.workspace.openTextDocument({
                        language: 'markdown',
                        content: result.data.prompt
                    });
                    
                    await vscode.window.showTextDocument(document);
                    vscode.window.showInformationMessage('Prompt contextual generado.');
                    
                    // Actualizar vista de prompts
                    state.providers.prompts.refresh();
                } else {
                    vscode.window.showErrorMessage(`Error al generar el prompt: ${result.error}`);
                }
                
                return result.success;
            });
        } catch (err) {
            vscode.window.showErrorMessage(`Error en la generación de prompt: ${err.message}`);
        }
    });
    
    // Comando: Mostrar documentación
    const showDocumentationCommand = vscode.commands.registerCommand('projectprompt.showDocumentation', async () => {
        if (!state.initialized) {
            vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
            return;
        }
        
        const projectPath = state.workspaceFolder;
        if (!projectPath) {
            vscode.window.showErrorMessage('No hay ninguna carpeta de proyecto abierta.');
            return;
        }
        
        // Verificar si existe documentación
        const docsPath = path.join(projectPath, '.project-prompt');
        if (!fs.existsSync(docsPath)) {
            const action = await vscode.window.showWarningMessage(
                'No se encontró documentación para este proyecto. ¿Desea generarla?',
                'Generar', 'Cancelar'
            );
            
            if (action === 'Generar') {
                vscode.commands.executeCommand('projectprompt.analyzeProject');
            }
            return;
        }
        
        // Buscar archivos de documentación
        const files = fs.readdirSync(docsPath).filter(file => file.endsWith('.md'));
        if (files.length === 0) {
            vscode.window.showInformationMessage('No se encontraron archivos de documentación.');
            return;
        }
        
        // Mostrar selector si hay múltiples archivos
        let selectedFile;
        if (files.length === 1) {
            selectedFile = files[0];
        } else {
            selectedFile = await vscode.window.showQuickPick(files, {
                placeHolder: 'Seleccione un archivo de documentación'
            });
            
            if (!selectedFile) return; // Usuario canceló
        }
        
        // Abrir el archivo de documentación
        const docUri = vscode.Uri.file(path.join(docsPath, selectedFile));
        const doc = await vscode.workspace.openTextDocument(docUri);
        await vscode.window.showTextDocument(doc);
    });
    
    // Comando: Generar tests
    const generateTestsCommand = vscode.commands.registerCommand('projectprompt.generateTests', async (resource) => {
        if (!state.initialized) {
            vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
            return;
        }
        
        // Verificar si es característica premium
        const isPremium = await checkPremiumFeature('test_generation');
        if (!isPremium) {
            const action = await vscode.window.showWarningMessage(
                'La generación de tests es una característica premium. ¿Desea saber más sobre los planes premium?',
                'Ver planes', 'Cancelar'
            );
            
            if (action === 'Ver planes') {
                vscode.commands.executeCommand('projectprompt.premium.showPlans');
            }
            return;
        }
        
        const target = resource?.fsPath;
        if (!target) {
            vscode.window.showErrorMessage('No se ha seleccionado ningún archivo.');
            return;
        }
        
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "ProjectPrompt: Generando tests...",
                cancellable: true
            }, async (progress) => {
                progress.report({ increment: 20, message: "Analizando código..." });
                
                const result = await runProjectPromptCommand(['premium', 'test-generator', target]);
                progress.report({ increment: 80, message: "Tests generados" });
                
                if (result.success) {
                    vscode.window.showInformationMessage(`Tests generados en ${result.data.outputDir}`);
                    
                    // Abrir el primer archivo de test generado
                    if (result.data.files && result.data.files.length > 0) {
                        const testUri = vscode.Uri.file(result.data.files[0]);
                        const doc = await vscode.workspace.openTextDocument(testUri);
                        await vscode.window.showTextDocument(doc);
                    }
                } else {
                    vscode.window.showErrorMessage(`Error al generar tests: ${result.error}`);
                }
                
                return result.success;
            });
        } catch (err) {
            vscode.window.showErrorMessage(`Error en la generación de tests: ${err.message}`);
        }
    });
    
    // Comando: Verificar completitud de característica
    const checkFeatureCompletenessCommand = vscode.commands.registerCommand(
        'projectprompt.checkFeatureCompleteness',
        async (featureName) => {
            if (!state.initialized) {
                vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
                return;
            }
            
            // Verificar si es característica premium
            const isPremium = await checkPremiumFeature('completeness_verification');
            if (!isPremium) {
                const action = await vscode.window.showWarningMessage(
                    'La verificación de completitud es una característica premium. ¿Desea saber más sobre los planes premium?',
                    'Ver planes', 'Cancelar'
                );
                
                if (action === 'Ver planes') {
                    vscode.commands.executeCommand('projectprompt.premium.showPlans');
                }
                return;
            }
            
            // Solicitar nombre de característica si no se proporcionó
            let feature = featureName;
            if (!feature) {
                feature = await vscode.window.showInputBox({
                    prompt: 'Ingrese el nombre de la característica a verificar'
                });
                
                if (!feature) return; // Usuario canceló
            }
            
            try {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: "ProjectPrompt: Verificando completitud...",
                    cancellable: true
                }, async (progress) => {
                    progress.report({ increment: 20, message: "Analizando..." });
                    
                    const result = await runProjectPromptCommand(['premium', 'verify-completeness', feature]);
                    progress.report({ increment: 80, message: "Verificación completada" });
                    
                    if (result.success) {
                        // Mostrar resultados en un panel
                        if (!state.panel) {
                            state.panel = new ProjectPromptPanel(context.extensionUri, state);
                        }
                        state.panel.reveal();
                        state.panel.updateContent('completeness', result.data);
                    } else {
                        vscode.window.showErrorMessage(`Error en la verificación: ${result.error}`);
                    }
                    
                    return result.success;
                });
            } catch (err) {
                vscode.window.showErrorMessage(`Error en la verificación: ${err.message}`);
            }
        }
    );
    
    // Comando: Mostrar dashboard
    const showDashboardCommand = vscode.commands.registerCommand('projectprompt.showDashboard', async () => {
        if (!state.initialized) {
            vscode.window.showWarningMessage('ProjectPrompt no está inicializado correctamente.');
            return;
        }
        
        const projectPath = state.workspaceFolder;
        if (!projectPath) {
            vscode.window.showErrorMessage('No hay ninguna carpeta de proyecto abierta.');
            return;
        }
        
        try {
            const isPremium = await checkPremiumFeature('project_dashboard');
            const command = isPremium ? ['premium', 'dashboard'] : ['dashboard'];
            
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "ProjectPrompt: Generando dashboard...",
                cancellable: true
            }, async (progress) => {
                progress.report({ increment: 30, message: "Recopilando métricas..." });
                
                const result = await runProjectPromptCommand([...command, projectPath, '--no-browser']);
                progress.report({ increment: 70, message: "Dashboard generado" });
                
                if (result.success && result.data.dashboardPath) {
                    // Abrir el dashboard en el editor
                    const dashboardUri = vscode.Uri.file(result.data.dashboardPath);
                    vscode.commands.executeCommand('vscode.open', dashboardUri);
                    vscode.window.showInformationMessage('Dashboard generado correctamente.');
                } else {
                    vscode.window.showErrorMessage(`Error al generar dashboard: ${result.error || 'Error desconocido'}`);
                }
                
                return result.success;
            });
        } catch (err) {
            vscode.window.showErrorMessage(`Error al generar dashboard: ${err.message}`);
        }
    });
    
    // Comando: Enviar prompt a GitHub Copilot
    const sendToCopilotCommand = vscode.commands.registerCommand('projectprompt.sendToCopilot', async (promptContent) => {
        if (!state.copilotAvailable) {
            vscode.window.showWarningMessage('GitHub Copilot no está disponible. Por favor, instale y configure la extensión de GitHub Copilot.');
            return;
        }
        
        if (!promptContent) {
            // Si no se proporciona un prompt, intentar obtenerlo del editor activo
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const selection = editor.selection;
                promptContent = editor.document.getText(selection);
            }
            
            if (!promptContent || promptContent.trim() === '') {
                vscode.window.showErrorMessage('No se ha proporcionado un prompt para enviar a GitHub Copilot.');
                return;
            }
        }
        
        // Enviar prompt a Copilot
        try {
            const hasChatPanel = await CopilotIntegration.openCopilotChatWithPrompt(promptContent);
            if (!hasChatPanel) {
                await CopilotIntegration.sendPromptToCopilot(promptContent);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error al comunicarse con GitHub Copilot: ${error.message}`);
        }
    });
    
    // Añadir comandos a las suscripciones
    context.subscriptions.push(
        showPanelCommand,
        analyzeProjectCommand,
        generatePromptCommand,
        showDocumentationCommand,
        generateTestsCommand,
        checkFeatureCompletenessCommand,
        showDashboardCommand,
        sendToCopilotCommand
    );
    
    // Auto-análisis al abrir (si está configurado)
    if (state.workspaceFolder && vscode.workspace.getConfiguration('projectprompt').get('autoAnalyzeOnOpen')) {
        vscode.commands.executeCommand('projectprompt.analyzeProject');
    }
    
    // Mostrar mensaje de bienvenida
    vscode.window.showInformationMessage('ProjectPrompt está listo. Use la paleta de comandos o el panel lateral para comenzar.');
    console.log('ProjectPrompt activado correctamente');
    
    // Verificar Python y dependencias automáticamente
    async function checkPythonInstallation(pythonPath) {
        try {
            const command = pythonPath || 'python3';
            execSync(`${command} --version`);
            return true;
        } catch (error) {
            try {
                execSync('python --version');
                return true;
            } catch (err) {
                return false;
            }
        }
    }
    
    async function checkProjectPromptInstallation() {
        try {
            const command = state.pythonPath || 'python3';
            execSync(`${command} -m pip show project-prompt`);
            return true;
        } catch (error) {
            try {
                execSync('python -m pip show project-prompt');
                return true;
            } catch (err) {
                return false;
            }
        }
    }
    
    async function installProjectPrompt() {
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Instalando ProjectPrompt...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20, message: "Descargando..." });
                
                const command = state.pythonPath || 'python3';
                execSync(`${command} -m pip install project-prompt`, { encoding: 'utf8' });
                
                progress.report({ increment: 80, message: "Instalación completada" });
                state.initialized = true;
                
                vscode.window.showInformationMessage('ProjectPrompt instalado correctamente.');
                return true;
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error al instalar ProjectPrompt: ${error.message}`);
            return false;
        }
    }
    
    async function runProjectPromptCommand(args) {
        try {
            const command = state.pythonPath || 'python3';
            const result = execSync(`${command} -m project-prompt ${args.join(' ')}`, { encoding: 'utf8' });
            
            try {
                // Intentar parsear como JSON
                const jsonData = JSON.parse(result);
                return { success: true, data: jsonData };
            } catch {
                // Si no es JSON, devolver el texto
                return { success: true, data: { output: result } };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async function checkPremiumFeature(featureName) {
        try {
            const command = state.pythonPath || 'python3';
            execSync(`${command} -m project-prompt subscription info --check-feature ${featureName}`, { encoding: 'utf8' });
            return true;
        } catch (error) {
            return false;
        }
    }
}

function deactivate() {
    console.log('ProjectPrompt se está desactivando...');
}

module.exports = {
    activate,
    deactivate
};
