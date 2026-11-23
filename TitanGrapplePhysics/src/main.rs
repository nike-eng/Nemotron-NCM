#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

const GRAVITY: f32 = -9.81;
const JUMP_STRENGTH: f32 = 10.0;
const COYOTE_TIME: f32 = 0.1;
const DASH_COOLDOWN: f32 = 1.0;
const GRAPPLE_SPEED: f32 = 20.0;

struct Player {
    position: (f32, f32),
    velocity: (f32, f32),
    on_ground: bool,
    coyote_timer: f32,
    dash_cooldown_timer: f32,
}

impl Player {
    fn new() -> Self {
        Player {
            position: (0.0, 0.0),
            velocity: (0.0, 0.0),
            on_ground: false,
            coyote_timer: 0.0,
            dash_cooldown_timer: 0.0,
        }
    }

    fn update(&mut self, dt: f32) {
        if self.on_ground {
            self.velocity.1 = 0.0;
        } else {
            self.velocity.1 += GRAVITY * dt;
        }

        self.position.0 += self.velocity.0 * dt;
        self.position.1 += self.velocity.1 * dt;

        if self.coyote_timer > 0.0 {
            self.coyote_timer -= dt;
        }

        if self.dash_cooldown_timer > 0.0 {
            self.dash_cooldown_timer -= dt;
        }
    }

    fn jump(&mut self) {
        if self.coyote_timer > 0.0 {
            self.velocity.1 = JUMP_STRENGTH;
            self.coyote_timer = 0.0;
        }
    }

    fn dash(&mut self, direction: (f32, f32)) {
        if self.dash_cooldown_timer <= 0.0 {
            self.velocity.0 += direction.0 * GRAPPLE_SPEED;
            self.velocity.1 += direction.1 * GRAPPLE_SPEED;
            self.dash_cooldown_timer = DASH_COOLDOWN;
        }
    }
}

fn main() {
    let mut player = Player::new();
    let dt = 1.0 / 60.0;

    loop {
        player.update(dt);

        // Example input handling
        if true { // Replace with actual jump condition
            player.jump();
        }
        if true { // Replace with actual dash condition
            player.dash((1.0, 0.0)); // Example direction
        }

        // Steamworks achievement logging
        // Assuming some function log_achievement exists
        // log_achievement("grappled_objective");

        // Break condition for demonstration
        if player.position.1 < -10.0 {
            break;
        }
    }
}