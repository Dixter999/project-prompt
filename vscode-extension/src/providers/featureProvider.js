// Feature Provider para VS Code
// Proporciona datos de características del proyecto para el TreeView

const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

class FeatureProvider {
    constructor(state) {
        this._state = state;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
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
        
        // Si no hay análisis, mostrar mensaje de placeholder
        if (!this._state.lastAnalysis) {
            const item = new vscode.TreeItem(
                'Analizar proyecto para ver características',
                vscode.TreeItemCollapsibleState.None
            );
            item.command = {
                command: 'projectprompt.analyzeProject',
                title: 'Analizar Proyecto'
            };
            return Promise.resolve([item]);
        }
        
        // Si ya se pasó un elemento, mostrar sus hijos (archivos de la característica)
        if (element) {
            return this._getFeatureFiles(element.feature);
        }
        
        // Obtener características del análisis
        const features = this._state.lastAnalysis.functionalities || [];
        if (features.length === 0) {
            const item = new vscode.TreeItem(
                'No se detectaron características',
                vscode.TreeItemCollapsibleState.None
            );
            return Promise.resolve([item]);
        }
        
        // Crear elementos de árbol para cada característica
        return Promise.resolve(
            features.map(feature => {
                const hasFiles = feature.files && feature.files.length > 0;
                const item = new vscode.TreeItem(
                    feature.name,
                    hasFiles ? 
                        vscode.TreeItemCollapsibleState.Collapsed : 
                        vscode.TreeItemCollapsibleState.None
                );
                
                item.tooltip = feature.description || feature.name;
                item.description = `${feature.confidence}% confianza`;
                item.iconPath = new vscode.ThemeIcon('symbol-class');
                item.feature = feature;
                
                // Añadir comando para verificar completitud
                item.command = {
                    command: 'projectprompt.checkFeatureCompleteness',
                    title: 'Verificar Completitud',
                    arguments: [feature.name]
                };
                
                return item;
            })
        );
    }
    
    /**
     * Obtiene los archivos asociados a una característica
     */
    _getFeatureFiles(feature) {
        if (!feature || !feature.files || feature.files.length === 0) {
            return Promise.resolve([]);
        }
        
        return Promise.resolve(
            feature.files.map(file => {
                const filename = path.basename(file);
                const item = new vscode.TreeItem(
                    filename,
                    vscode.TreeItemCollapsibleState.None
                );
                
                item.tooltip = file;
                item.resourceUri = vscode.Uri.file(file);
                
                // Icono según extensión de archivo
                const extension = path.extname(file).toLowerCase();
                if (['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs'].includes(extension)) {
                    item.iconPath = new vscode.ThemeIcon('symbol-file');
                } else if (['.md', '.txt', '.rst'].includes(extension)) {
                    item.iconPath = new vscode.ThemeIcon('symbol-text');
                } else if (['.json', '.yaml', '.yml', '.xml', '.csv'].includes(extension)) {
                    item.iconPath = new vscode.ThemeIcon('symbol-structure');
                } else {
                    item.iconPath = new vscode.ThemeIcon('file');
                }
                
                // Comando para abrir el archivo
                item.command = {
                    command: 'vscode.open',
                    title: 'Abrir Archivo',
                    arguments: [vscode.Uri.file(file)]
                };
                
                return item;
            })
        );
    }
}

module.exports = FeatureProvider;
