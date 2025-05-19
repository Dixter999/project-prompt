/**
 * Core game engine class
 * This is the main entry point for the game engine
 */
export class GameEngine {
  private systems: GameSystem[] = [];
  private entities: Map<string, Entity> = new Map();
  private isRunning: boolean = false;
  private lastTimestamp: number = 0;

  /**
   * Initialize the game engine
   * @param config Engine configuration object
   */
  constructor(private config: GameEngineConfig) {
    console.log(`Initializing game engine with config:`, config);
  }

  /**
   * Add a system to the engine
   * @param system System to add
   */
  public addSystem(system: GameSystem): void {
    this.systems.push(system);
    system.initialize(this);
    console.log(`Added system: ${system.getName()}`);
  }

  /**
   * Register an entity with the engine
   * @param entity Entity to register
   * @returns The registered entity
   */
  public registerEntity(entity: Entity): Entity {
    this.entities.set(entity.id, entity);
    console.log(`Registered entity: ${entity.id}`);
    return entity;
  }

  /**
   * Remove an entity from the engine
   * @param entityId ID of the entity to remove
   */
  public removeEntity(entityId: string): void {
    this.entities.delete(entityId);
    console.log(`Removed entity: ${entityId}`);
  }

  /**
   * Get an entity by ID
   * @param entityId ID of the entity
   * @returns Entity or undefined if not found
   */
  public getEntity(entityId: string): Entity | undefined {
    return this.entities.get(entityId);
  }

  /**
   * Start the game loop
   */
  public start(): void {
    if (this.isRunning) {
      return;
    }

    this.isRunning = true;
    this.lastTimestamp = performance.now();
    
    // Initialize all systems
    this.systems.forEach(system => system.initialize(this));
    
    // Start the game loop
    requestAnimationFrame(this.gameLoop.bind(this));
    console.log(`Game engine started`);
  }

  /**
   * Stop the game loop
   */
  public stop(): void {
    this.isRunning = false;
    console.log(`Game engine stopped`);
  }

  /**
   * Main game loop
   * @param timestamp Current timestamp
   */
  private gameLoop(timestamp: number): void {
    if (!this.isRunning) {
      return;
    }

    const deltaTime = (timestamp - this.lastTimestamp) / 1000;
    this.lastTimestamp = timestamp;

    // Update all systems
    this.systems.forEach(system => system.update(deltaTime));
    
    // Request next frame
    requestAnimationFrame(this.gameLoop.bind(this));
  }
}

/**
 * Game engine configuration
 */
export interface GameEngineConfig {
  canvasId?: string;
  width: number;
  height: number;
  debug?: boolean;
}

/**
 * Base class for game systems
 */
export abstract class GameSystem {
  protected engine: GameEngine | null = null;

  /**
   * Initialize the system with the game engine
   * @param engine Game engine instance
   */
  public initialize(engine: GameEngine): void {
    this.engine = engine;
  }

  /**
   * Update the system
   * @param deltaTime Time since last update in seconds
   */
  public abstract update(deltaTime: number): void;

  /**
   * Get the name of the system
   * @returns System name
   */
  public abstract getName(): string;
}

/**
 * Base entity class
 */
export class Entity {
  public readonly id: string;
  private components: Map<string, Component> = new Map();

  /**
   * Create a new entity
   * @param id Optional ID, will generate a random UUID if not provided
   */
  constructor(id?: string) {
    this.id = id || crypto.randomUUID();
  }

  /**
   * Add a component to the entity
   * @param component Component to add
   * @returns This entity for chaining
   */
  public addComponent(component: Component): Entity {
    this.components.set(component.type, component);
    return this;
  }

  /**
   * Remove a component from the entity
   * @param type Type of component to remove
   * @returns This entity for chaining
   */
  public removeComponent(type: string): Entity {
    this.components.delete(type);
    return this;
  }

  /**
   * Get a component by type
   * @param type Type of component to get
   * @returns Component or undefined if not found
   */
  public getComponent<T extends Component>(type: string): T | undefined {
    return this.components.get(type) as T;
  }

  /**
   * Check if entity has a component
   * @param type Type of component to check for
   * @returns True if entity has component
   */
  public hasComponent(type: string): boolean {
    return this.components.has(type);
  }
}

/**
 * Base component interface
 */
export interface Component {
  type: string;
}
