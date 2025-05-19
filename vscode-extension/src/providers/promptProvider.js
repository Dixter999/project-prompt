// Prompt Provider para VS Code
// Proporciona datos de prompts generados para el TreeView

const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

class PromptProvider {
    constructor(state) {
        this._state = state;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this._promptHistory = [];
    }
    
    /**
     * Refresca los datos del proveedor
     */
    refresh() {
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
        if (!this._state.workspaceFolder) {
            return Promise.resolve([]);
        }
        
        // Cargar historial de prompts
        this._loadPromptHistory();
        
        if (this._promptHistory.length === 0) {
            const item = new vscode.TreeItem(
                'No hay prompts generados',
                vscode.TreeItemCollapsibleState.None
            );
            
            item.command = {
                command: 'projectprompt.generatePrompt',
                title: 'Generar Prompt'
            };
            
            return Promise.resolve([item]);
        }
        
        // Si hay un elemento padre, mostrar los detalles del prompt
        if (element) {
            // Si ya es un elemento hoja, no tiene hijos
            return Promise.resolve([]);
        }
        
        // Mostrar categorías de prompts
        const categories = [
            {
                id: 'recent',
                label: 'Prompts Recientes',
                prompts: this._promptHistory.slice(0, 5) // Mostrar solo los 5 más recientes
            },
            {
                id: 'contextual',
                label: 'Prompts Contextuales',
                prompts: this._promptHistory.filter(p => p.type === 'contextual')
            },
            {
                id: 'implementation',
                label: 'Prompts de Implementación',
                prompts: this._promptHistory.filter(p => p.type === 'implementation')
            }
        ];
        
        return Promise.resolve(
            categories.map(category => {
                const isEmpty = category.prompts.length === 0;
                const item = new vscode.TreeItem(
                    category.label,
                    isEmpty ? 
                        vscode.TreeItemCollapsibleState.None : 
                        vscode.TreeItemCollapsibleState.Collapsed
                );
                
                item.contextValue = 'promptCategory';
                item.category = category;
                
                return item;
            })
        );
    }
    
    /**
     * Carga el historial de prompts desde el almacenamiento
     */
    _loadPromptHistory() {
        try {
            const projectPath = this._state.workspaceFolder;
            
            if (!projectPath) {
                this._promptHistory = [];
                return;
            }
            
            const promptsDir = path.join(projectPath, '.project-prompt', 'prompts');
            
            if (!fs.existsSync(promptsDir)) {
                this._promptHistory = [];
                return;
            }
            
            const files = fs.readdirSync(promptsDir)
                .filter(file => file.endsWith('.json'))
                .sort((a, b) => {
                    // Ordenar por fecha de modificación (más recientes primero)
                    const statA = fs.statSync(path.join(promptsDir, a));
                    const statB = fs.statSync(path.join(promptsDir, b));
                    return statB.mtime.getTime() - statA.mtime.getTime();
                });
            
            this._promptHistory = files.map(file => {
                try {
                    const filePath = path.join(promptsDir, file);
                    const content = fs.readFileSync(filePath, 'utf8');
                    const data = JSON.parse(content);
                    
                    return {
                        id: path.basename(file, '.json'),
                        title: data.title || 'Prompt sin título',
                        type: data.type || 'contextual',
                        date: data.date || new Date().toISOString(),
                        target: data.target || '',
                        content: data.prompt || '',
                        filePath
                    };
                } catch (err) {
                    console.error(`Error al leer prompt ${file}:`, err);
                    return null;
                }
            }).filter(Boolean); // Filtrar prompts no válidos
        } catch (error) {
            console.error('Error al cargar historial de prompts:', error);
            this._promptHistory = [];
        }
    }
    
    /**
     * Registra un nuevo prompt en el historial
     */
    registerPrompt(prompt) {
        try {
            const projectPath = this._state.workspaceFolder;
            
            if (!projectPath) return false;
            
            const promptsDir = path.join(projectPath, '.project-prompt', 'prompts');
            
            // Crear directorio si no existe
            if (!fs.existsSync(promptsDir)) {
                fs.mkdirSync(promptsDir, { recursive: true });
            }
            
            // Generar ID único para el prompt
            const timestamp = Date.now();
            const id = `prompt_${timestamp}`;
            
            // Preparar datos del prompt
            const promptData = {
                title: prompt.title || 'Prompt sin título',
                type: prompt.type || 'contextual',
                date: new Date().toISOString(),
                target: prompt.target || '',
                prompt: prompt.content || ''
            };
            
            // Guardar archivo
            const filePath = path.join(promptsDir, `${id}.json`);
            fs.writeFileSync(filePath, JSON.stringify(promptData, null, 2), 'utf8');
            
            // Actualizar historial en memoria
            this._promptHistory.unshift({
                id,
                ...promptData,
                filePath
            });
            
            // Refrescar vista
            this.refresh();
            
            return true;
        } catch (error) {
            console.error('Error al registrar prompt:', error);
            return false;
        }
    }
}

module.exports = PromptProvider;
