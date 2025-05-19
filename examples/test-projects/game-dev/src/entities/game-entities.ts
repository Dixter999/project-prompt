import { Entity, Component } from '../core/engine';

/**
 * Transform component for positioning entities in the game world
 */
export class TransformComponent implements Component {
  public readonly type = 'transform';
  
  /**
   * Create a new transform component
   * @param x X position
   * @param y Y position
   * @param rotation Rotation in radians
   * @param scaleX X scale factor
   * @param scaleY Y scale factor
   */
  constructor(
    public x: number = 0,
    public y: number = 0,
    public rotation: number = 0,
    public scaleX: number = 1,
    public scaleY: number = 1
  ) {}
  
  /**
   * Set the position
   * @param x X position
   * @param y Y position
   * @returns This component for chaining
   */
  public setPosition(x: number, y: number): TransformComponent {
    this.x = x;
    this.y = y;
    return this;
  }
  
  /**
   * Set the rotation
   * @param rotation Rotation in radians
   * @returns This component for chaining
   */
  public setRotation(rotation: number): TransformComponent {
    this.rotation = rotation;
    return this;
  }
  
  /**
   * Set the scale
   * @param scaleX X scale factor
   * @param scaleY Y scale factor
   * @returns This component for chaining
   */
  public setScale(scaleX: number, scaleY: number): TransformComponent {
    this.scaleX = scaleX;
    this.scaleY = scaleY;
    return this;
  }
}

/**
 * Sprite component for rendering entities
 */
export class SpriteComponent implements Component {
  public readonly type = 'sprite';
  
  /**
   * Create a new sprite component
   * @param imageUrl URL of the sprite image
   * @param width Width of the sprite
   * @param height Height of the sprite
   * @param visible Whether the sprite is visible
   */
  constructor(
    public imageUrl: string,
    public width: number,
    public height: number,
    public visible: boolean = true
  ) {}
  
  /**
   * Set the visibility
   * @param visible Visibility flag
   * @returns This component for chaining
   */
  public setVisible(visible: boolean): SpriteComponent {
    this.visible = visible;
    return this;
  }
}

/**
 * Player entity with input handling
 */
export class PlayerEntity extends Entity {
  /**
   * Create a new player entity
   * @param x Initial X position
   * @param y Initial Y position
   * @param spriteUrl URL of the player sprite
   */
  constructor(x: number = 0, y: number = 0, spriteUrl: string = 'assets/player.png') {
    super('player');
    
    // Add transform component
    this.addComponent(new TransformComponent(x, y));
    
    // Add sprite component
    this.addComponent(new SpriteComponent(spriteUrl, 64, 64));
    
    // Add collision component
    this.addComponent(new CollisionComponent(32));
    
    // Add health component
    this.addComponent(new HealthComponent(100));
  }
}

/**
 * Collision component for physics interactions
 */
export class CollisionComponent implements Component {
  public readonly type = 'collision';
  
  /**
   * Create a new collision component
   * @param radius Collision radius
   * @param collisionGroup Collision group for filtering
   * @param solid Whether the entity is solid (blocks movement)
   */
  constructor(
    public radius: number,
    public collisionGroup: string = 'default',
    public solid: boolean = true
  ) {}
  
  /**
   * Set whether the entity is solid
   * @param solid Solid flag
   * @returns This component for chaining
   */
  public setSolid(solid: boolean): CollisionComponent {
    this.solid = solid;
    return this;
  }
}

/**
 * Health component for entities with health
 */
export class HealthComponent implements Component {
  public readonly type = 'health';
  private currentHealth: number;
  
  /**
   * Create a new health component
   * @param maxHealth Maximum health
   * @param currentHealth Current health (defaults to maxHealth)
   * @param invulnerable Whether the entity is invulnerable
   */
  constructor(
    public maxHealth: number,
    currentHealth?: number,
    public invulnerable: boolean = false
  ) {
    this.currentHealth = currentHealth !== undefined ? currentHealth : maxHealth;
  }
  
  /**
   * Get current health
   */
  public getHealth(): number {
    return this.currentHealth;
  }
  
  /**
   * Take damage
   * @param amount Amount of damage
   * @returns Current health after damage
   */
  public takeDamage(amount: number): number {
    if (!this.invulnerable && amount > 0) {
      this.currentHealth = Math.max(0, this.currentHealth - amount);
    }
    return this.currentHealth;
  }
  
  /**
   * Heal the entity
   * @param amount Amount to heal
   * @returns Current health after healing
   */
  public heal(amount: number): number {
    if (amount > 0) {
      this.currentHealth = Math.min(this.maxHealth, this.currentHealth + amount);
    }
    return this.currentHealth;
  }
  
  /**
   * Check if the entity is dead
   * @returns True if health is 0
   */
  public isDead(): boolean {
    return this.currentHealth <= 0;
  }
}
