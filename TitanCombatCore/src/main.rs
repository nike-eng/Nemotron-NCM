#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

struct Projectile {
    position: (usize, usize),
    velocity: (isize, isize),
}

struct Entity {
    id: usize,
    position: (usize, usize),
}

struct World {
    entities: Vec<Entity>,
    projectiles: Vec<Projectile>,
}

impl World {
    fn new() -> Self {
        World {
            entities: vec![
                Entity { id: 0, position: ARENA_SPAWNS[0] },
                Entity { id: 1, position: ARENA_SPAWNS[1] },
                Entity { id: 2, position: ARENA_SPAWNS[2] },
            ],
            projectiles: vec![],
        }
    }

    fn update(&mut self) {
        let mut to_remove = Vec::new();
        for (i, projectile) in self.projectiles.iter_mut().enumerate() {
            projectile.position.0 = (projectile.position.0 as isize + projectile.velocity.0) as usize;
            projectile.position.1 = (projectile.position.1 as isize + projectile.velocity.1) as usize;
            if self.check_collision(projectile.position) {
                println!("Hit detected!");
                // Unlock Steam 'Sharpshooter' achievement here
                to_remove.push(i);
            }
        }
        for index in to_remove.iter().rev() {
            self.projectiles.remove(*index);
        }
    }

    fn check_collision(&self, position: (usize, usize)) -> bool {
        for entity in &self.entities {
            if entity.position == position {
                return true;
            }
        }
        false
    }

    fn spawn_projectile(&mut self, position: (usize, usize), velocity: (isize, isize)) {
        self.projectiles.push(Projectile { position, velocity });
    }
}

fn main() {
    let mut world = World::new();
    world.spawn_projectile((0, 0), (1, 1));

    loop {
        world.update();
        std::thread::sleep(std::time::Duration::from_millis(16));
    }
}