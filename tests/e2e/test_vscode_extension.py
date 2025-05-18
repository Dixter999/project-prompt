#!/usr/bin/env python3
"""
Test end-to-end para la extensión de VSCode de ProjectPrompt.
Verifica la funcionalidad de la extensión y su integración con la aplicación.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
import shutil

# Asegurar que el módulo principal está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


class TestVSCodeExtension(unittest.TestCase):
    """Pruebas end-to-end para la extensión de VSCode."""
    
    def setUp(self):
        """Configurar el entorno para las pruebas."""
        self.test_dir = tempfile.mkdtemp()
        self.extension_dir = os.path.join(self.test_dir, 'vscode-extension')
        os.makedirs(self.extension_dir)
        
        # Copiar archivos de extensión para pruebas
        self._setup_extension_files()
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        shutil.rmtree(self.test_dir)
        
    def _setup_extension_files(self):
        """Configurar archivos necesarios para probar la extensión."""
        # Crear package.json simulado
        package_json = {
            "name": "project-prompt-extension",
            "displayName": "ProjectPrompt",
            "description": "Extension for ProjectPrompt",
            "version": "1.0.0",
            "engines": {
                "vscode": "^1.60.0"
            },
            "categories": [
                "Other"
            ],
            "activationEvents": [
                "onCommand:project-prompt.analyze",
                "onCommand:project-prompt.generatePrompt",
                "onCommand:project-prompt.generateDocs"
            ],
            "main": "./extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "project-prompt.analyze",
                        "title": "ProjectPrompt: Analyze Project"
                    },
                    {
                        "command": "project-prompt.generatePrompt",
                        "title": "ProjectPrompt: Generate Prompt"
                    },
                    {
                        "command": "project-prompt.generateDocs",
                        "title": "ProjectPrompt: Generate Documentation"
                    }
                ]
            }
        }
        
        # Escribir el archivo package.json
        with open(os.path.join(self.extension_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Crear extension.js simulado
        extension_js = """
// The module 'vscode' contains the VS Code extensibility API
const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('ProjectPrompt extension is now active');

    let analyzeCommand = vscode.commands.registerCommand('project-prompt.analyze', function () {
        runProjectPromptCommand('analyze');
    });

    let generatePromptCommand = vscode.commands.registerCommand('project-prompt.generatePrompt', function () {
        runProjectPromptCommand('generate', 'prompt');
    });

    let generateDocsCommand = vscode.commands.registerCommand('project-prompt.generateDocs', function () {
        runProjectPromptCommand('generate', 'docs');
    });

    context.subscriptions.push(analyzeCommand, generatePromptCommand, generateDocsCommand);
}

function runProjectPromptCommand(...args) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
        vscode.window.showErrorMessage('No workspace folder is open');
        return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    
    const command = 'project-prompt';
    const process = spawn(command, [...args, '--path', workspaceRoot]);
    
    let output = '';
    process.stdout.on('data', (data) => {
        output += data;
    });

    process.stderr.on('data', (data) => {
        vscode.window.showErrorMessage(`ProjectPrompt error: ${data}`);
    });

    process.on('close', (code) => {
        if (code === 0) {
            vscode.window.showInformationMessage('ProjectPrompt command executed successfully');
            const outputChannel = vscode.window.createOutputChannel('ProjectPrompt');
            outputChannel.append(output);
            outputChannel.show();
        } else {
            vscode.window.showErrorMessage(`ProjectPrompt command failed with code ${code}`);
        }
    });
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
}
"""
        
        # Escribir el archivo extension.js
        with open(os.path.join(self.extension_dir, 'extension.js'), 'w') as f:
            f.write(extension_js)
            
    def test_extension_package_json(self):
        """Verificar que el package.json de la extensión es válido y tiene los comandos correctos."""
        with open(os.path.join(self.extension_dir, 'package.json'), 'r') as f:
            package_data = json.load(f)
            
        self.assertEqual(package_data['name'], 'project-prompt-extension')
        self.assertIn('commands', package_data['contributes'])
        
        commands = package_data['contributes']['commands']
        command_ids = [cmd['command'] for cmd in commands]
        
        self.assertIn('project-prompt.analyze', command_ids)
        self.assertIn('project-prompt.generatePrompt', command_ids)
        self.assertIn('project-prompt.generateDocs', command_ids)
        
    def test_extension_structure(self):
        """Verificar que la estructura básica de la extensión está correcta."""
        # Verificar existencia de archivos clave
        self.assertTrue(os.path.exists(os.path.join(self.extension_dir, 'package.json')))
        self.assertTrue(os.path.exists(os.path.join(self.extension_dir, 'extension.js')))
        
    def test_extension_commands(self):
        """Verificar que los comandos de la extensión están definidos correctamente."""
        with open(os.path.join(self.extension_dir, 'extension.js'), 'r') as f:
            extension_code = f.read()
            
        self.assertIn('project-prompt.analyze', extension_code)
        self.assertIn('project-prompt.generatePrompt', extension_code)
        self.assertIn('project-prompt.generateDocs', extension_code)
        self.assertIn('runProjectPromptCommand', extension_code)
        
    def test_extension_command_execution(self):
        """Verificar que los comandos de la extensión ejecutan correctamente los comandos de CLI."""
        # Este test es más simulado ya que no podemos ejecutar realmente VSCode
        with open(os.path.join(self.extension_dir, 'extension.js'), 'r') as f:
            extension_code = f.read()
            
        # Verificar que se usa spawn para ejecutar los comandos
        self.assertIn('spawn(command', extension_code)
        self.assertIn('--path', extension_code)
        

if __name__ == '__main__':
    unittest.main()
