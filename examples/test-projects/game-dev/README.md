# Game Development Project

A template project for game development with modern architecture and best practices.

## Structure

- `src/`: Source code for the game
  - `core/`: Core game engine components
  - `entities/`: Game entities and objects
  - `systems/`: Game systems (physics, AI, etc.)
  - `assets/`: Asset loaders and managers
  - `scenes/`: Game scenes and levels
  - `ui/`: User interface components
  - `utils/`: Utility functions and helpers
  - `physics/`: Physics simulation and collision detection
  - `audio/`: Audio management and effects
- `docs/`: Documentation
- `tests/`: Unit and integration tests

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Game Architecture

This project follows the Entity-Component-System (ECS) architecture for efficient game development:

- **Entities**: Game objects with unique IDs
- **Components**: Data containers attached to entities
- **Systems**: Logic processors that act on entities with specific components

## Assets

Place game assets in the appropriate directories:

- `public/assets/images/`: Sprites and textures
- `public/assets/audio/`: Sound effects and music
- `public/assets/models/`: 3D models
- `public/assets/fonts/`: Game fonts

## Technical Documentation

For technical details, refer to the [Documentation](./docs/README.md).

## Testing

Run the tests with:

```bash
npm test
```

## Build and Deploy

To build for production:

```bash
npm run build
```

The build output will be in the `dist/` directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
