// NCM Open-World Sector Topology (Seed #99)
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
pub const ARENA_SPAWNS: [(usize, usize); 9] = [(0, 7), (1, 4), (2, 1), (3, 6), (4, 3), (5, 0), (6, 5), (7, 2), (8, 8)];
pub const ARENA_OBJECTIVES: [(usize, usize); 9] = [(0, 2), (1, 8), (2, 5), (3, 1), (4, 7), (5, 4), (6, 0), (7, 6), (8, 3)];
pub const COVER_PILLAR_COUNT: usize = 18;
pub fn compute_state_hash(data: &[u8]) -> String {
    let mut h = DefaultHasher::new();
    data.hash(&mut h);
    format!("{:016x}", h.finish())
}
