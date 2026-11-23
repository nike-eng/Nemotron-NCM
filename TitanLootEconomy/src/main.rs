#![allow(dead_code, unused_variables)]

mod arena_map;
use arena_map::*;

struct Inventory {
    resources: u32,
    weapons: Vec<String>,
}

impl Inventory {
    fn new() -> Self {
        Inventory {
            resources: 0,
            weapons: vec!["Basic Gun".to_string()],
        }
    }

    fn drop_resource(&mut self, amount: u32) {
        self.resources += amount;
    }

    fn upgrade_weapon(&mut self, weapon_name: &str) {
        if let Some(pos) = self.weapons.iter().position(|w| w == weapon_name) {
            self.weapons[pos] = format!("{}+", weapon_name);
        }
    }
}

fn main() {
    let mut inventory = Inventory::new();

    for &(x, y) in &ARENA_OBJECTIVES {
        // Simulate dropping resources at objectives
        inventory.drop_resource(10);

        // Simulate upgrading weapons at objectives
        inventory.upgrade_weapon("Basic Gun");
    }

    println!("Resources: {}", inventory.resources);
    println!("Weapons: {:?}", inventory.weapons);
}