#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

const ARENA_SPAWNS: [(usize, usize); 10] = [
    (0, 0), (1, 1), (2, 2), (3, 3), (4, 4),
    (5, 5), (6, 6), (7, 7), (8, 8), (9, 9),
];

const PHYSICS_DT: f32 = 1.0 / 60.0;

struct Entity {
    position: (f32, f32),
    velocity: (f32, f32),
}

struct World {
    entities: Vec<Entity>,
}

impl World {
    fn new() -> Self {
        World { entities: Vec::new() }
    }

    fn spawn_entities(&mut self) {
        for &(x, y) in &ARENA_SPAWNS {
            self.entities.push(Entity {
                position: (x as f32, y as f32),
                velocity: (0.0, 0.0),
            });
        }
    }

    fn update_physics(&mut self) {
        for entity in &mut self.entities {
            entity.position.0 += entity.velocity.0 * PHYSICS_DT;
            entity.position.1 += entity.velocity.1 * PHYSICS_DT;
        }
    }

    fn log_achievement(achievement_name: &str) {
        println!("Achievement unlocked: {}", achievement_name);
    }
}

fn main() {
    let mut world = World::new();
    world.spawn_entities();

    for _ in 0..60 {
        world.update_physics();
    }

    World::log_achievement("60Hz ECS Loop Completed");
}