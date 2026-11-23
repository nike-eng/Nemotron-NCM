#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

const MAX_SNAPSHOTS: usize = 10;
const PLAYERS: usize = 4;

#[derive(Copy, Clone)]
struct Player {
    position: (usize, usize),
    health: u8,
}

#[derive(Copy, Clone)]
struct Snapshot {
    players: [Player; PLAYERS],
    objective_status: [bool; ARENA_OBJECTIVES.len()],
}

struct Game {
    snapshots: [Snapshot; MAX_SNAPSHOTS],
    current_snapshot_index: usize,
}

impl Game {
    fn new() -> Self {
        let mut initial_snapshot = Snapshot {
            players: [Player { position: (0, 0), health: 100 }; PLAYERS],
            objective_status: [false; ARENA_OBJECTIVES.len()],
        };

        for (i, spawn) in ARENA_SPAWNS.iter().enumerate() {
            initial_snapshot.players[i].position = *spawn;
        }

        Game {
            snapshots: [initial_snapshot; MAX_SNAPSHOTS],
            current_snapshot_index: 0,
        }
    }

    fn take_snapshot(&mut self) {
        self.snapshots[self.current_snapshot_index] = self.snapshots[(self.current_snapshot_index + MAX_SNAPSHOTS - 1) % MAX_SNAPSHOTS];
        self.current_snapshot_index = (self.current_snapshot_index + 1) % MAX_SNAPSHOTS;
    }

    fn rollback(&mut self, steps: usize) {
        self.current_snapshot_index = (self.current_snapshot_index + MAX_SNAPSHOTS - steps) % MAX_SNAPSHOTS;
    }
}

fn main() {
    let mut game = Game::new();

    // Simulate some game actions
    game.take_snapshot();
    game.take_snapshot();

    // Rollback to previous state
    game.rollback(1);

    // Continue simulation
    game.take_snapshot();
}