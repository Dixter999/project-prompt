// Premium Provider para VS Code
// Proporciona datos de características premium para el TreeView

const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class PremiumProvider {
    constructor(state) {
        this._state = state;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this._subscriptionInfo = null;
        
        // Cargar información de suscripción
        this._loadSubscriptionInfo();
    }
    
    /**
     * Refresca los datos del proveedor
     */
    refresh() {
        this._loadSubscriptionInfo();
        this._onDidChangeTreeData.fire();
    }
    
    /**
     * Obtiene los elementos raíz para el TreeView
     */
    getTreeItem(element) {
        return element;
    }
    
    /**
     * Obtiene los elementos hijo para un elemento dado
     */
    getChildren(element) {
        // Si ya se pasó un elemento, mostrar sus hijos (features)
        if (element && element.contextValue === 'premiumCategory') {
            return this._getPremiumFeatures(element.category);
        }
        
        // Verificar si la información de suscripción está disponible
        if (!this._subscriptionInfo) {
            const item = new vscode.TreeItem(
                'Cargando información de suscripción...',
                vscode.TreeItemCollapsibleState.None
            );
            
            this._loadSubscriptionInfo(); // Intentar cargar de nuevo
            return Promise.resolve([item]);
        }
        
        // Categorías principales: Suscripción y Características Premium
        const categories = [
            {
                id: 'subscription',
                label: `Suscripción: ${this._subscriptionInfo.type.toUpperCase()}`,
                collapsible: vscode.TreeItemCollapsibleState.None,
                icon: this._subscriptionInfo.isPremium ? 'verified' : 'unverified'
            },
            {
                id: 'features',
                label: 'Características Premium',
                collapsible: vscode.TreeItemCollapsibleState.Collapsed,
                icon: 'star'
            },
            {
                id: 'plans',
                label: 'Ver planes disponibles',
                collapsible: vscode.TreeItemCollapsibleState.None,
                icon: 'key',
                command: 'projectprompt.premium.showPlans'
            }
        ];
        
        return Promise.resolve(
            categories.map(category => {
                const item = new vscode.TreeItem(
                    category.label,
                    category.collapsible
                );
                
                item.iconPath = new vscode.ThemeIcon(category.icon);
                item.category = category;
                item.contextValue = 'premiumCategory';
                
                // Añadir comando si existe
                if (category.command) {
                    item.command = {
                        command: category.command,
                        title: category.label
                    };
                }
                
                return item;
            })
        );
    }
    
    /**
     * Obtiene las características premium
     */
    _getPremiumFeatures(category) {
        if (!category || category.id !== 'features') {
            return Promise.resolve([]);
        }
        
        // Lista de características premium
        const features = [
            {
                id: 'project_dashboard',
                label: 'Dashboard de proyecto',
                description: this._isFeatureAvailable('project_dashboard') ? 'Disponible' : 'Requiere suscripción',
                available: this._isFeatureAvailable('project_dashboard'),
                command: 'projectprompt.showDashboard'
            },
            {
                id: 'test_generation',
                label: 'Generación de tests',
                description: this._isFeatureAvailable('test_generation') ? 'Disponible' : 'Requiere suscripción',
                available: this._isFeatureAvailable('test_generation'),
                command: 'projectprompt.generateTests'
            },
            {
                id: 'completeness_verification',
                label: 'Verificación de completitud',
                description: this._isFeatureAvailable('completeness_verification') ? 'Disponible' : 'Requiere suscripción',
                available: this._isFeatureAvailable('completeness_verification'),
                command: 'projectprompt.checkFeatureCompleteness'
            },
            {
                id: 'implementation_prompts',
                label: 'Asistente de implementación',
                description: this._isFeatureAvailable('implementation_prompts') ? 'Disponible' : 'Requiere suscripción',
                available: this._isFeatureAvailable('implementation_prompts'),
                command: 'projectprompt.premium.implementation'
            }
        ];
        
        return Promise.resolve(
            features.map(feature => {
                const item = new vscode.TreeItem(
                    feature.label,
                    vscode.TreeItemCollapsibleState.None
                );
                
                item.description = feature.description;
                item.iconPath = new vscode.ThemeIcon(feature.available ? 'check' : 'lock');
                
                // Añadir comando solo si la característica está disponible
                if (feature.available && feature.command) {
                    item.command = {
                        command: feature.command,
                        title: feature.label
                    };
                }
                
                return item;
            })
        );
    }
    
    /**
     * Carga la información de suscripción
     */
    async _loadSubscriptionInfo() {
        try {
            const command = this._state.pythonPath || 'python3';
            const result = execSync(
                `${command} -m project-prompt subscription info --json`,
                { encoding: 'utf8' }
            );
            
            try {
                // Parsear resultado como JSON
                const data = JSON.parse(result);
                this._subscriptionInfo = {
                    type: data.subscription_type || 'free',
                    isPremium: data.is_premium || false,
                    features: data.available_features || [],
                    limits: data.limits || {}
                };
            } catch (error) {
                console.error('Error al parsear información de suscripción:', error);
                this._subscriptionInfo = {
                    type: 'free',
                    isPremium: false,
                    features: []
                };
            }
        } catch (error) {
            console.error('Error al obtener información de suscripción:', error);
            
            // Establecer valores por defecto
            this._subscriptionInfo = {
                type: 'free',
                isPremium: false,
                features: []
            };
        }
    }
    
    /**
     * Verifica si una característica premium está disponible
     */
    _isFeatureAvailable(featureId) {
        if (!this._subscriptionInfo || !this._subscriptionInfo.features) {
            return false;
        }
        
        return this._subscriptionInfo.features.includes(featureId);
    }
    
    /**
     * Registra un comando para mostrar planes premium
     */
    registerCommands(context) {
        const showPlansCommand = vscode.commands.registerCommand('projectprompt.premium.showPlans', async () => {
            try {
                // Obtener información de planes
                const command = this._state.pythonPath || 'python3';
                const result = execSync(`${command} -m project-prompt subscription plans --json`, { encoding: 'utf8' });
                
                try {
                    const plans = JSON.parse(result);
                    
                    // Mostrar planes en un webview
                    const panel = vscode.window.createWebviewPanel(
                        'projectpromptPlans',
                        'ProjectPrompt: Planes Premium',
                        vscode.ViewColumn.One,
                        { enableScripts: true }
                    );
                    
                    panel.webview.html = this._generatePlansHTML(plans);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error al procesar planes: ${error.message}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Error al obtener planes: ${error.message}`);
            }
        });
        
        const activateLicenseCommand = vscode.commands.registerCommand('projectprompt.premium.activateLicense', async () => {
            const licenseKey = await vscode.window.showInputBox({
                placeHolder: 'XXXXX-XXXXX-XXXXX-XXXXX-XXXXX',
                prompt: 'Ingrese su clave de licencia premium'
            });
            
            if (!licenseKey) return;
            
            try {
                const command = this._state.pythonPath || 'python3';
                execSync(`${command} -m project-prompt subscription activate ${licenseKey}`, { encoding: 'utf8' });
                
                vscode.window.showInformationMessage('Licencia activada correctamente');
                this.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Error al activar licencia: ${error.message}`);
            }
        });
        
        const deactivateLicenseCommand = vscode.commands.registerCommand('projectprompt.premium.deactivateLicense', async () => {
            const confirm = await vscode.window.showWarningMessage(
                '¿Está seguro que desea desactivar su licencia premium?',
                { modal: true },
                'Sí', 'No'
            );
            
            if (confirm !== 'Sí') return;
            
            try {
                const command = this._state.pythonPath || 'python3';
                execSync(`${command} -m project-prompt subscription deactivate`, { encoding: 'utf8' });
                
                vscode.window.showInformationMessage('Licencia desactivada correctamente');
                this.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Error al desactivar licencia: ${error.message}`);
            }
        });
        
        const implementationCommand = vscode.commands.registerCommand('projectprompt.premium.implementation', async () => {
            const functionality = await vscode.window.showInputBox({
                prompt: 'Nombre de la funcionalidad a implementar'
            });
            
            if (!functionality) return;
            
            try {
                const command = this._state.pythonPath || 'python3';
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: "Generando guía de implementación...",
                    cancellable: true
                }, async (progress) => {
                    try {
                        const result = execSync(
                            `${command} -m project-prompt premium implementation "${functionality}" --path "${this._state.workspaceFolder}" --json`, 
                            { encoding: 'utf8' }
                        );
                        
                        const data = JSON.parse(result);
                        
                        // Crear documento con la guía
                        const document = await vscode.workspace.openTextDocument({
                            language: 'markdown',
                            content: data.guide || 'No se pudo generar la guía de implementación.'
                        });
                        
                        await vscode.window.showTextDocument(document);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Error al generar guía: ${error.message}`);
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
            }
        });
        
        context.subscriptions.push(showPlansCommand, activateLicenseCommand, deactivateLicenseCommand, implementationCommand);
    }
    
    /**
     * Genera HTML para mostrar planes premium
     */
    _generatePlansHTML(plans) {
        return `
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Planes Premium ProjectPrompt</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: var(--vscode-foreground);
                        background-color: var(--vscode-editor-background);
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .header h1 {
                        margin-bottom: 5px;
                    }
                    .plans-container {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin-top: 20px;
                    }
                    .plan-card {
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 5px;
                        padding: 20px;
                    }
                    .plan-name {
                        font-size: 1.5em;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }
                    .plan-price {
                        font-size: 1.2em;
                        margin-bottom: 15px;
                    }
                    .features-list {
                        list-style-type: none;
                        padding: 0;
                    }
                    .features-list li {
                        padding: 5px 0;
                    }
                    .feature-check {
                        color: #3fb950;
                        margin-right: 8px;
                    }
                    .feature-cross {
                        color: #f85149;
                        margin-right: 8px;
                    }
                    .cta-button {
                        display: inline-block;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        padding: 8px 16px;
                        border-radius: 3px;
                        font-size: 14px;
                        cursor: pointer;
                        margin-top: 15px;
                        text-decoration: none;
                    }
                    .plan-card.highlight {
                        border: 2px solid var(--vscode-button-background);
                        position: relative;
                    }
                    .highlight-badge {
                        position: absolute;
                        top: -10px;
                        right: -10px;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>ProjectPrompt Premium</h1>
                    <p>Desbloquea características avanzadas para mejorar tu productividad</p>
                </div>
                
                <div class="plans-container">
                    ${plans.map((plan, index) => `
                        <div class="plan-card ${index === 2 ? 'highlight' : ''}">
                            ${index === 2 ? '<span class="highlight-badge">POPULAR</span>' : ''}
                            <div class="plan-name">${plan.name}</div>
                            <div class="plan-price">${plan.price}</div>
                            
                            <ul class="features-list">
                                ${plan.features.map(feature => 
                                    `<li><span class="feature-check">✓</span> ${feature}</li>`
                                ).join('')}
                            </ul>
                            
                            <a href="https://www.projectprompt.dev/pricing" class="cta-button">
                                Obtener ${plan.name}
                            </a>
                        </div>
                    `).join('')}
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p>¿Ya tienes una licencia? <a href="javascript:void(0);" onclick="activateLicense()">Activar ahora</a></p>
                </div>
                
                <script>
                    function activateLicense() {
                        const vscode = acquireVsCodeApi();
                        vscode.postMessage({
                            command: 'activateLicense'
                        });
                    }
                    
                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.command) {
                            case 'refreshPlans':
                                location.reload();
                                break;
                        }
                    });
                </script>
            </body>
            </html>
        `;
    }
}

module.exports = PremiumProvider;
