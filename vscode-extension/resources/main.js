// ProjectPrompt VSCode Extension - WebView Script

// Comunicación con el host de VSCode
const vscode = acquireVsCodeApi();

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    setupTabNavigation();
    setupActionButtons();
    setupFeatureButtons();
    setupPromptButtons();
    setupDocumentationButtons();
    setupCopilotButtons();
});

/**
 * Configura la navegación por pestañas
 */
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Desactivar todas las pestañas
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.style.display = 'none');
            
            // Activar pestaña seleccionada
            button.classList.add('active');
            const tabId = `${button.dataset.tab}-tab`;
            document.getElementById(tabId).style.display = 'block';
        });
    });
}

/**
 * Configura los botones de acción principales
 */
function setupActionButtons() {
    // Botón de análisis
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'analyze' });
        });
    }
    
    // Botón de prompt
    const promptBtn = document.getElementById('prompt-btn');
    if (promptBtn) {
        promptBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'generatePrompt' });
        });
    }
    
    // Botón de documentación
    const docsBtn = document.getElementById('docs-btn');
    if (docsBtn) {
        docsBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'showDocs' });
        });
    }
    
    // Botón de dashboard completo
    const dashboardBtn = document.getElementById('show-dashboard-btn');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'showDashboard' });
        });
    }
    
    // Botón de upgrade a premium
    const upgradeBtn = document.getElementById('upgrade-premium-btn');
    if (upgradeBtn) {
        upgradeBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'upgradeToPremium' });
        });
    }
}

/**
 * Configura los botones de características
 */
function setupFeatureButtons() {
    // Botones de verificación de completitud
    const checkButtons = document.querySelectorAll('.feature-btn.check-btn');
    checkButtons.forEach(button => {
        button.addEventListener('click', () => {
            const feature = button.dataset.feature;
            vscode.postMessage({ 
                command: 'checkCompleteness',
                feature: feature
            });
        });
    });
    
    // Botones de generación de tests
    const testButtons = document.querySelectorAll('.feature-btn.test-btn');
    testButtons.forEach(button => {
        button.addEventListener('click', () => {
            const feature = button.dataset.feature;
            vscode.postMessage({
                command: 'generateTests',
                feature: feature
            });
        });
    });
    
    // Enlaces a archivos
    const fileLinks = document.querySelectorAll('.file-link');
    fileLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const filePath = link.dataset.path;
            vscode.postMessage({
                command: 'openFile',
                file: filePath
            });
        });
    });
}

/**
 * Configura los botones de prompts
 */
function setupPromptButtons() {
    // Botón de prompt para archivo
    const filePromptBtn = document.getElementById('file-prompt-btn');
    if (filePromptBtn) {
        filePromptBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'generatePrompt', type: 'file' });
        });
    }
    
    // Botón de prompt para funcionalidad
    const featurePromptBtn = document.getElementById('feature-prompt-btn');
    if (featurePromptBtn) {
        featurePromptBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'generatePrompt', type: 'feature' });
        });
    }
    
    // Botón de prompt para selección
    const selectionPromptBtn = document.getElementById('selection-prompt-btn');
    if (selectionPromptBtn) {
        selectionPromptBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'generatePrompt', type: 'selection' });
        });
    }
    
    // Botón de prompt de implementación
    const implPromptBtn = document.getElementById('implementation-prompt-btn');
    if (implPromptBtn) {
        implPromptBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'generateImplementationPrompt' });
        });
    }
}

/**
 * Configura los botones de documentación
 */
function setupDocumentationButtons() {
    // Botón de ver documentación
    const viewDocsBtn = document.getElementById('view-docs-btn');
    if (viewDocsBtn) {
        viewDocsBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'showDocs' });
        });
    }
    
    // Botón de generar documentación
    const generateDocsBtn = document.getElementById('generate-docs-btn');
    if (generateDocsBtn) {
        generateDocsBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'generateDocs' });
        });
    }
    
    // Botón de documentación premium
    const premiumDocsBtn = document.getElementById('premium-docs-btn');
    if (premiumDocsBtn) {
        premiumDocsBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'upgradeToPremium' });
        });
    }
}

/**
 * Actualiza secciones específicas del panel con nuevos datos
 */
window.addEventListener('message', event => {
    const message = event.data;
    
    if (message.command === 'update') {
        const section = message.section;
        const data = message.data;
        
        switch (section) {
            case 'analysis':
                updateDashboard(data);
                break;
            case 'features':
                updateFeatures(data);
                break;
            case 'prompts':
                updatePrompts(data);
                break;
            case 'completeness':
                updateCompleteness(data);
                break;
        }
    }
});

/**
 * Actualiza el panel de dashboard con nuevos datos
 */
function updateDashboard(data) {
    // Implementación para actualizar el dashboard
}

/**
 * Actualiza la vista de características
 */
function updateFeatures(data) {
    // Implementación para actualizar la vista de características
}

/**
 * Actualiza la vista de prompts
 */
function updatePrompts(data) {
    // Implementación para actualizar prompts
}

/**
 * Actualiza el reporte de completitud
 */
function updateCompleteness(data) {
    // Implementación para actualizar el reporte de completitud
}
