#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

#[derive(Debug, Clone, Copy)]
struct Sphere {
    position: (f32, f32, f32),
    radius: f32,
}

#[derive(Debug, Clone, Copy)]
struct Pillar {
    position: (f32, f32, f32),
    radius: f32,
    height: f32,
}

fn swept_sphere_vs_pillar_collision(sphere: &Sphere, pillar: &Pillar, move_vector: (f32, f32, f32)) -> bool {
    let mut start = sphere.position;
    let end = (
        start.0 + move_vector.0,
        start.1 + move_vector.1,
        start.2 + move_vector.2,
    );

    let sphere_to_pillar = (
        pillar.position.0 - start.0,
        pillar.position.1 - start.1,
        pillar.position.2 - start.2,
    );

    let dot = sphere_to_pillar.0 * move_vector.0 + sphere_to_pillar.1 * move_vector.1 + sphere_to_pillar.2 * move_vector.2;
    if dot < 0.0 {
        return false;
    }

    let sphere_to_pillar_squared = sphere_to_pillar.0 * sphere_to_pillar.0 + sphere_to_pillar.1 * sphere_to_pillar.1 + sphere_to_pillar.2 * sphere_to_pillar.2;
    let radius_sum = sphere.radius + pillar.radius;
    if sphere_to_pillar_squared > radius_sum * radius_sum {
        let c = sphere_to_pillar_squared - radius_sum * radius_sum;
        if c > 0.0 {
            return false;
        }
    }

    let f = dot * dot - c;
    if f < 0.0 {
        return false;
    }

    let t = dot - f.sqrt();
    if t >= 0.0 && t <= 1.0 {
        let closest_point = (
            start.0 + move_vector.0 * t,
            start.1 + move_vector.1 * t,
            start.2 + move_vector.2 * t,
        );

        let closest_to_pillar = (
            pillar.position.0 - closest_point.0,
            pillar.position.1 - closest_point.1,
            pillar.position.2 - closest_point.2,
        );

        let closest_to_pillar_squared = closest_to_pillar.0 * closest_to_pillar.0 + closest_to_pillar.1 * closest_to_pillar.1 + closest_to_pillar.2 * closest_to_pillar.2;
        if closest_to_pillar_squared <= pillar.radius * pillar.radius {
            return true;
        }
    }

    false
}

fn rollback_state_hash(state: &[(f32, f32, f32)]) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut hasher = DefaultHasher::new();
    state.hash(&mut hasher);
    hasher.finish()
}

fn test_swept_sphere_vs_pillar_collision() {
    let sphere = Sphere { position: (0.0, 0.0, 0.0), radius: 1.0 };
    let pillar = Pillar { position: (5.0, 0.0, 0.0), radius: 1.0, height: 10.0 };

    assert_eq!(swept_sphere_vs_pillar_collision(&sphere, &pillar, (1.0, 0.0, 0.0)), true);
    assert_eq!(swept_sphere_vs_pillar_collision(&sphere, &pillar, (4.0, 0.0, 0.0)), false);
}

fn test_rollback_state_hash() {
    let state1 = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)];
    let state2 = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)];
    let state3 = [(0.0, 0.0, 0.0), (2.0, 2.0, 2.0)];

    assert_eq!(rollback_state_hash(&state1), rollback_state_hash(&state2));
    assert_ne!(rollback_state_hash(&state1), rollback_state_hash(&state3));
}

fn test_steam_achievement_unlock() {
    // Placeholder for Steam achievement unlock logic
    let state = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)];
    let hash = rollback_state_hash(&state);

    // Example condition for unlocking an achievement
    if hash == 123456789 {
        println!("Achievement unlocked!");
    } else {
        println!("Achievement not unlocked.");
    }
}

fn main() {
    test_swept_sphere_vs_pillar_collision();
    test_rollback_state_hash();
    test_steam_achievement_unlock();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_collision_detection() {
        let sphere = Sphere { position: (0.0, 0.0, 0.0), radius: 1.0 };
        let pillar = Pillar { position: (5.0, 0.0, 0.0), radius: 1.0, height: 10.0 };

        assert!(swept_sphere_vs_pillar_collision(&sphere, &pillar, (1.0, 0.0, 0.0)));
        assert!(!swept_sphere_vs_pillar_collision(&sphere, &pillar, (4.0, 0.0, 0.0)));
    }

    #[test