#![allow(dead_code, unused_variables)]

pub const ARENA_SPAWNS: [(usize, usize); 9] = [(0, 4), (1, 1), (2, 7), (3, 3), (4, 0), (5, 6), (6, 2), (7, 8), (8, 5)];
pub const ARENA_OBJECTIVES: [(usize, usize); 9] = [(0, 8), (1, 5), (2, 2), (3, 7), (4, 4), (5, 1), (6, 6), (7, 3), (8, 0)];
pub const COVER_PILLAR_COUNT: usize = 18;

#[derive(Debug)]
struct Player {
    position: (f32, f32),
    velocity: (f32, f32),
}

fn update_physics(players: &mut [Player]) {
    for player in players.iter_mut() {
        player.position.0 += player.velocity.0 * 1.0 / 60.0;
        player.position.1 += player.velocity.1 * 1.0 / 60.0;
    }
}

fn main() {
    let mut players = vec![
        Player { position: (0.0, 0.0), velocity: (1.0, 0.0) },
        Player { position: (0.0, 0.0), velocity: (-1.0, 0.0) },
        Player { position: (0.0, 0.0), velocity: (0.0, 1.0) },
        Player { position: (0.0, 0.0), velocity: (0.0, -1.0) },
    ];

    update_physics(&mut players);

    for player in players {
        println!("Player Position: {:?}", player.position);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_arena_spawns_length() {
        assert!(ARENA_SPAWNS.len() >= 4);
    }

    #[test]
    fn test_physics_tick() {
        let mut players = vec![
            Player { position: (0.0, 0.0), velocity: (1.0, 0.0) },
            Player { position: (0.0, 0.0), velocity: (-1.0, 0.0) },
            Player { position: (0.0, 0.0), velocity: (0.0, 1.0) },
            Player { position: (0.0, 0.0), velocity: (0.0, -1.0) },
        ];

        update_physics(&mut players);

        for player in players {
            assert_ne!(player.position, (0.0, 0.0));
        }
    }
}