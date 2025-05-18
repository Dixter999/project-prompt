// Documentation Provider para VS Code
// Proporciona datos de documentación del proyecto para el TreeView

const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

class DocumentationProvider {
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
        
        const projectPath = this._state.workspaceFolder;
        const docsPath = path.join(projectPath, '.project-prompt');
        
        // Verificar si el directorio de documentación existe
        if (!fs.existsSync(docsPath)) {
            const item = new vscode.TreeItem(
                'No hay documentación generada',
                vscode.TreeItemCollapsibleState.None
            );
            item.command = {
                command: 'projectprompt.showPanel',
                title: 'Mostrar Panel'
            };
            return Promise.resolve([item]);
        }
        
        // Si ya se pasó un elemento, es una categoría y queremos sus archivos
        if (element && element.contextValue === 'docCategory') {
            return this._getDocumentationFiles(element.category);
        }
        
        // Categorías de documentación
        const categories = [
            { 
                id: 'overview', 
                label: 'Visión General', 
                pattern: '*_analysis_*.md',
                icon: 'symbol-file'
            },
            { 
                id: 'features', 
                label: 'Características',
                pattern: '*_feature_*.md',
                icon: 'symbol-class'
            },
            { 
                id: 'architecture', 
                label: 'Arquitectura',
                pattern: '*_architecture_*.md',
                icon: 'symbol-structure'
            },
            { 
                id: 'tests', 
                label: 'Tests',
                pattern: '*_tests_*.md',
                icon: 'beaker'
            },
            { 
                id: 'other', 
                label: 'Otros Documentos',
                pattern: '*.md',
                icon: 'file'
            }
        ];
        
        return Promise.resolve(
            categories.map(category => {
                const item = new vscode.TreeItem(
                    category.label,
                    vscode.TreeItemCollapsibleState.Collapsed
                );
                item.iconPath = new vscode.ThemeIcon(category.icon);
                item.category = category;
                item.contextValue = 'docCategory';
                return item;
            })
        );
    }
    
    /**
     * Obtiene los archivos de documentación de una categoría
     */
    _getDocumentationFiles(category) {
        if (!category) return Promise.resolve([]);
        
        const projectPath = this._state.workspaceFolder;
        const docsPath = path.join(projectPath, '.project-prompt');
        
        try {
            // Leer directorio y aplicar filtro según categoría
            const files = fs.readdirSync(docsPath)
                .filter(file => {
                    // Primero verificar si es archivo markdown
                    if (!file.endsWith('.md')) return false;
                    
                    // Aplicar patrón específico de la categoría
                    if (category.id === 'other') {
                        // Para "Otros", incluir archivos que no sean de las otras categorías
                        return !file.includes('_analysis_') && 
                               !file.includes('_feature_') && 
                               !file.includes('_architecture_') &&
                               !file.includes('_tests_');
                    } else {
                        // Para categorías específicas, verificar según patrón
                        const pattern = category.pattern.replace('*', '');
                        return file.includes(pattern);
                    }
                });
            
            if (files.length === 0) {
                const item = new vscode.TreeItem(
                    `No hay documentos de ${category.label.toLowerCase()}`,
                    vscode.TreeItemCollapsibleState.None
                );
                return Promise.resolve([item]);
            }
            
            return Promise.resolve(
                files.map(file => {
                    const filePath = path.join(docsPath, file);
                    const item = new vscode.TreeItem(file);
                    
                    item.tooltip = `Abrir ${file}`;
                    item.command = {
                        command: 'vscode.open',
                        title: 'Abrir Documento',
                        arguments: [vscode.Uri.file(filePath)]
                    };
                    
                    return item;
                })
            );
        } catch (error) {
            const item = new vscode.TreeItem(
                `Error al leer documentación: ${error.message}`,
                vscode.TreeItemCollapsibleState.None
            );
            return Promise.resolve([item]);
        }
    }
}

module.exports = DocumentationProvider;
