#![allow(dead_code, unused_variables, unused_imports)]
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
fn compute_state_hash(s: &[u8]) -> String {
    let mut h = DefaultHasher::new();
    s.hash(&mut h);
    format!("{:016x}", h.finish())
}


mod arena_map;
use arena_map::*;

struct Sphere {
    position: (f64, f64, f64),
    radius: f64,
}

struct Pillar {
    position: (f64, f64, f64),
    radius: f64,
    height: f64,
}

fn sphere_pillar_collision(sphere: &Sphere, pillar: &Pillar) -> bool {
    let dx = sphere.position.0 - pillar.position.0;
    let dy = sphere.position.1 - pillar.position.1;
    let dz = sphere.position.2 - pillar.position.2;

    let distance_squared = dx * dx + dy * dy + dz * dz;
    let closest_distance_squared = distance_squared - dz * dz;

    let sphere_radius_squared = sphere.radius * sphere.radius;
    let pillar_radius_squared = pillar.radius * pillar.radius;

    closest_distance_squared <= (sphere_radius_squared + pillar_radius_squared)
}

fn rollback_state_hash(state: &[u8]) -> String {
    compute_state_hash(state)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sphere_pillar_collision() {
        let sphere = Sphere {
            position: (0.0, 0.0, 0.0),
            radius: 1.0,
        };

        let pillar = Pillar {
            position: (1.0, 0.0, 0.0),
            radius: 1.0,
            height: 10.0,
        };

        assert!(sphere_pillar_collision(&sphere, &pillar));
    }

    #[test]
    fn test_rollback_state_hash() {
        let state = [1, 2, 3, 4];
        assert_eq!(rollback_state_hash(&state), "7229c8d86d1c632f");
    }
}

fn main() {
    // Example usage
    let sphere = Sphere {
        position: (0.0, 0.0, 0.0),
        radius: 1.0,
    };

    let pillar = Pillar {
        position: (1.0, 0.0, 0.0),
        radius: 1.0,
        height: 10.0,
    };

    if sphere_pillar_collision(&sphere, &pillar) {
        println!("Collision detected!");
    } else {
        println!("No collision.");
    }
}