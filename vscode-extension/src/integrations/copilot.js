// ProjectPrompt integration with GitHub Copilot
const vscode = require('vscode');

/**
 * Provides integration functionality with GitHub Copilot
 */
class CopilotIntegration {
    /**
     * Initialize the Copilot integration
     * @param {Object} state Global extension state
     * @returns {Boolean} True if Copilot is available
     */
    static async initialize(state) {
        try {
            // Check if GitHub Copilot extension is installed
            const extension = vscode.extensions.getExtension('GitHub.copilot');
            state.copilotAvailable = !!extension;
            
            if (!state.copilotAvailable) {
                console.log('GitHub Copilot extension not found.');
                return false;
            }
            
            // Check if the extension is active
            if (!extension.isActive) {
                await extension.activate();
            }
            
            console.log('GitHub Copilot integration initialized successfully.');
            return true;
        } catch (error) {
            console.error('Error initializing GitHub Copilot integration:', error);
            state.copilotAvailable = false;
            return false;
        }
    }
    
    /**
     * Sends a prompt to GitHub Copilot through VSCode's interface
     * @param {String} prompt The prompt to send to Copilot
     */
    static async sendPromptToCopilot(prompt) {
        try {
            // Create a temporary file with the prompt
            const doc = await vscode.workspace.openTextDocument({
                language: 'plaintext',
                content: `// ProjectPrompt generated Copilot prompt:\n${prompt}\n\n`
            });
            
            // Show the document and position cursor at the end
            const editor = await vscode.window.showTextDocument(doc);
            const position = new vscode.Position(doc.lineCount, 0);
            editor.selection = new vscode.Selection(position, position);
            
            // Trigger Copilot inline suggestion
            await vscode.commands.executeCommand('editor.action.inlineSuggest.trigger');
            
            return true;
        } catch (error) {
            console.error('Error sending prompt to GitHub Copilot:', error);
            vscode.window.showErrorMessage('Error sending prompt to GitHub Copilot. Please make sure Copilot is properly set up.');
            return false;
        }
    }
    
    /**
     * Creates and shows a ChatPanel with the given prompt (if Copilot Chat is available)
     * @param {String} prompt The prompt for Copilot Chat
     */
    static async openCopilotChatWithPrompt(prompt) {
        try {
            // Check if Copilot Chat command is available
            const commands = await vscode.commands.getCommands();
            const hasCopilotChat = commands.includes('github.copilot.chat.startSession');
            
            if (!hasCopilotChat) {
                vscode.window.showInformationMessage('Copilot Chat no está disponible. Se utilizará la sugerencia inline.');
                return this.sendPromptToCopilot(prompt);
            }
            
            // Open Copilot Chat and insert the prompt
            await vscode.commands.executeCommand('github.copilot.chat.startSession');
            
            // Wait a bit for the chat panel to open
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Try to send the text to the active chat input
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor && activeEditor.document.fileName.includes('Copilot Chat')) {
                await activeEditor.edit(editBuilder => {
                    const position = new vscode.Position(0, 0);
                    editBuilder.insert(position, prompt);
                });
                
                // Send the message
                await vscode.commands.executeCommand('github.copilot.chat.sendQuery');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error opening Copilot Chat with prompt:', error);
            return false;
        }
    }
}

module.exports = CopilotIntegration;
