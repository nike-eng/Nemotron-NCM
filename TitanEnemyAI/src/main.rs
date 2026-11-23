#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

struct Position {
    x: usize,
    y: usize,
}

struct Velocity {
    dx: isize,
    dy: isize,
}

struct State {
    current: String,
    target: Option<Position>,
}

struct Enemy {
    position: Position,
    velocity: Velocity,
    state: State,
}

impl Enemy {
    fn new(position: Position) -> Self {
        Enemy {
            position,
            velocity: Velocity { dx: 0, dy: 0 },
            state: State {
                current: "Patrol".to_string(),
                target: None,
            },
        }
    }

    fn update(&mut self) {
        match self.state.current.as_str() {
            "Patrol" => self.patrol(),
            "SeekCover" => self.seek_cover(),
            _ => {}
        }
    }

    fn patrol(&mut self) {
        // Simple patrol logic
        self.velocity.dx = if self.position.x < ARENA_SPAWNS[0].0 { 1 } else { -1 };
        self.velocity.dy = if self.position.y < ARENA_SPAWNS[0].1 { 1 } else { -1 };
        self.move_enemy();
    }

    fn seek_cover(&mut self) {
        // Seek cover logic
        self.state.target = Some(Position {
            x: ARENA_OBJECTIVES[0].0,
            y: ARENA_OBJECTIVES[0].1,
        });
        self.move_enemy();
    }

    fn move_enemy(&mut self) {
        self.position.x = (self.position.x as isize + self.velocity.dx) as usize;
        self.position.y = (self.position.y as isize + self.velocity.dy) as usize;
    }
}

fn log_achievement(achievement_name: &str) {
    // Placeholder for Steamworks achievement logging
    println!("Achievement logged: {}", achievement_name);
}

fn main() {
    let mut enemies = vec![
        Enemy::new(Position { x: 0, y: 0 }),
        Enemy::new(Position { x: 1, y: 7 }),
        Enemy::new(Position { x: 2, y: 3 }),
    ];

    for _ in 0..120 { // Simulate 2 seconds at 60Hz
        for enemy in enemies.iter_mut() {
            enemy.update();
        }
    }

    log_achievement("EnemyPatrolComplete");
}