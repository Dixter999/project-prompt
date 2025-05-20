// Entry point for the VS Code extension

const panel = require('./panel');
const providers = {
    featureProvider: require('./providers/featureProvider'),
    documentationProvider: require('./providers/documentationProvider'),
    promptProvider: require('./providers/promptProvider'),
    premiumProvider: require('./providers/premiumProvider'),
};
const integrations = {
    copilot: require('./integrations/copilot'),
};

module.exports = {
    panel,
    providers,
    integrations,
};
