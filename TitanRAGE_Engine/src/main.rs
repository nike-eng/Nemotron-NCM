// src/main.rs
mod arena_map;
use arena_map::*;

fn main() {
    // Example usage of the arena map functions
    println!("Arena Spawns: {:?}", ARENA_SPAWNS);
    println!("Arena Objectives: {:?}", ARENA_OBJECTIVES);
    println!("Cover Pillar Count: {}", COVER_PILLAR_COUNT);

    let data = b"example_data";
    let hash = compute_state_hash(data);
    println!("State Hash: {}", hash);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sector_streaming() {
        // Add your sector streaming tests here
        assert_eq!(ARENA_SPAWNS.len(), 9);
        assert_eq!(ARENA_OBJECTIVES.len(), 9);
        assert_eq!(COVER_PILLAR_COUNT, 18);
    }

    #[test]
    fn test_compute_state_hash() {
        let data = b"example_data";
        let expected_hash = "b1e1d8c9f0a1b2c3d4e5f6a7b8c9d0e1"; // Replace with actual expected hash
        let computed_hash = compute_state_hash(data);
        assert_eq!(computed_hash, expected_hash);
    }
}