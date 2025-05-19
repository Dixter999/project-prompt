import { GameSystem, GameEngine, Entity } from '../core/engine';
import { TransformComponent, SpriteComponent } from '../entities/game-entities';

/**
 * System for rendering game entities to a canvas
 */
export class RenderSystem extends GameSystem {
  private canvas: HTMLCanvasElement | null = null;
  private context: CanvasRenderingContext2D | null = null;
  private sprites: Map<string, HTMLImageElement> = new Map();
  private loading: Map<string, boolean> = new Map();

  /**
   * Initialize the render system
   * @param engine Game engine instance
   */
  public initialize(engine: GameEngine): void {
    super.initialize(engine);

    // Get canvas element
    const canvasId = (this.engine as any).config?.canvasId || 'gameCanvas';
    this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
    
    if (!this.canvas) {
      console.error(`Canvas with ID "${canvasId}" not found, creating it`);
      this.canvas = document.createElement('canvas');
      this.canvas.id = canvasId;
      this.canvas.width = (this.engine as any).config?.width || 800;
      this.canvas.height = (this.engine as any).config?.height || 600;
      document.body.appendChild(this.canvas);
    }

    // Get rendering context
    this.context = this.canvas.getContext('2d');
    
    if (!this.context) {
      console.error('Failed to get canvas rendering context');
      return;
    }

    console.log(`Render system initialized with canvas: ${canvasId}`);
  }

  /**
   * Update the render system
   * @param deltaTime Time since last update in seconds
   */
  public update(deltaTime: number): void {
    if (!this.context || !this.canvas) {
      return;
    }

    // Clear the canvas
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Get all entities with transform and sprite components
    if (!this.engine) {
      return;
    }
    
    // We would normally have a way to query entities by component, but for simplicity,
    // we're assuming we can iterate all entities from the engine
    const entities = Array.from((this.engine as any).entities.values());
    
    // Sort entities by layer (assuming we had a layer system)
    // For now, we'll just render them in the order they come
    
    // Render each entity
    for (const entity of entities) {
      this.renderEntity(entity);
    }
    
    // Debug rendering if enabled
    if ((this.engine as any).config?.debug) {
      this.renderDebugInfo();
    }
  }

  /**
   * Render a single entity
   * @param entity Entity to render
   */
  private renderEntity(entity: Entity): void {
    if (!this.context) {
      return;
    }

    // Get required components
    const transform = entity.getComponent<TransformComponent>('transform');
    const sprite = entity.getComponent<SpriteComponent>('sprite');

    // Skip rendering if entity doesn't have required components or sprite is not visible
    if (!transform || !sprite || !sprite.visible) {
      return;
    }

    // Load sprite image if needed
    if (!this.sprites.has(sprite.imageUrl) && !this.loading.get(sprite.imageUrl)) {
      this.loadSprite(sprite.imageUrl);
      return;
    }

    // Get sprite image
    const image = this.sprites.get(sprite.imageUrl);
    
    // Skip if image isn't loaded yet
    if (!image) {
      return;
    }

    // Apply transform
    this.context.save();
    this.context.translate(transform.x, transform.y);
    this.context.rotate(transform.rotation);
    this.context.scale(transform.scaleX, transform.scaleY);

    // Draw sprite
    this.context.drawImage(
      image,
      -sprite.width / 2,
      -sprite.height / 2,
      sprite.width,
      sprite.height
    );

    // Restore context
    this.context.restore();
  }

  /**
   * Load a sprite image
   * @param url URL of the sprite image
   */
  private loadSprite(url: string): void {
    // Mark as loading
    this.loading.set(url, true);

    // Create image element
    const image = new Image();
    
    // Set up load handlers
    image.onload = () => {
      this.sprites.set(url, image);
      this.loading.set(url, false);
      console.log(`Loaded sprite: ${url}`);
    };
    
    image.onerror = () => {
      console.error(`Failed to load sprite: ${url}`);
      this.loading.set(url, false);
    };
    
    // Start loading
    image.src = url;
  }

  /**
   * Render debug information
   */
  private renderDebugInfo(): void {
    if (!this.context || !this.canvas) {
      return;
    }

    // Get FPS
    const fps = Math.round(1 / (this.engine as any).lastDeltaTime);

    // Draw FPS counter
    this.context.save();
    this.context.fillStyle = 'white';
    this.context.font = '16px monospace';
    this.context.fillText(`FPS: ${fps}`, 10, 20);
    
    // Draw entity count
    const entityCount = (this.engine as any).entities.size;
    this.context.fillText(`Entities: ${entityCount}`, 10, 40);
    
    this.context.restore();
  }

  /**
   * Get the name of this system
   * @returns System name
   */
  public getName(): string {
    return 'RenderSystem';
  }
}
