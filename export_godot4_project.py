import os, sys, zipfile, subprocess
sys.path.insert(0, "/kaggle/working/AI_Cyberdeck")

from phase2_fusion import LiveNCMCoprocessor
from cloud_brain import ask_free_cloud_coder
import auto_sync
from kaggle_secrets import UserSecretsClient

PROJ = "/kaggle/working/AI_Cyberdeck/TitanRAGE_Godot4"
os.makedirs(f"{PROJ}/scripts", exist_ok=True)
os.makedirs(f"{PROJ}/scenes", exist_ok=True)

# 1. NCM Spatial Architect solves 9x9 3D World Topology
bp = LiveNCMCoprocessor().generate_arena_blueprint(seed_idx=108)

# 2. Generate & Verify Godot 4 Player + Tactical Camera + Custom Procedural Animation Controller
player_gd = ask_free_cloud_coder(
    "You are a senior Godot 4.3 3D gameplay engineer. Output ONLY valid GDScript 2.0 with no markdown.",
    "Write player.gd extending CharacterBody3D with WASD/touch movement, sprint speed boost, jump gravity, and procedural walk bobbing animation on child node $Mesh."
)
with open(f"{PROJ}/scripts/player.gd", "w") as f:
    f.write(player_gd)

# 3. Generate & Verify Helicopter Spotlight Pursuit AI
heli_gd = ask_free_cloud_coder(
    "You are a senior Godot 4.3 3D AI engineer. Output ONLY valid GDScript 2.0 with no markdown.",
    "Write heli_ai.gd extending Node3D that orbits above the arena, tracks @export var target: Node3D smoothly, and aims child SpotLight3D at the target."
)
with open(f"{PROJ}/scripts/heli_ai.gd", "w") as f:
    f.write(heli_gd)

# Validate GDScript syntax via gdparse if installed
for gd in ["player.gd", "heli_ai.gd"]:
    res = subprocess.run(["gdparse", f"{PROJ}/scripts/{gd}"], capture_output=True, text=True)
    print(f"GDScript Check ({gd}):", "PASS" if res.returncode == 0 else res.stderr[:120])

# 4. Write Godot 4 project.godot
with open(f"{PROJ}/project.godot", "w") as f:
    f.write('config_version=5\n\n[application]\nconfig/name="TitanRAGE 3D Arena"\nrun/main_scene="res://scenes/main_arena.tscn"\nconfig/features=PackedStringArray("4.3", "GL Compatibility")\n')

# 5. Build Real Godot 4 3D Scene (.tscn) with PBR Environment, Volumetric Fog, NCM Pillars & Animated Rigs
nodes = [
    '[gd_scene load_steps=7 format=3]',
    '[ext_resource type="Script" path="res://scripts/player.gd" id="1"]',
    '[ext_resource type="Script" path="res://scripts/heli_ai.gd" id="2"]',
    '[sub_resource type="Environment" id="Env_1"]',
    'background_mode = 1',
    'background_color = Color(0.06, 0.09, 0.16, 1)',
    'ambient_light_source = 2',
    'ambient_light_color = Color(0.35, 0.45, 0.65, 1)',
    'fog_enabled = true',
    'fog_light_color = Color(0.12, 0.18, 0.28, 1)',
    'fog_density = 0.025',
    '[sub_resource type="BoxMesh" id="GroundMesh"]',
    'size = Vector3(24, 0.5, 24)',
    '[sub_resource type="BoxMesh" id="PillarMesh"]',
    'size = Vector3(1.1, 3.0, 1.1)',
    '[sub_resource type="CapsuleMesh" id="PlayerMesh"]',
    '[sub_resource type="BoxMesh" id="HeliMesh"]',
    'size = Vector3(1.8, 0.7, 3.2)',
    '[node name="TitanRAGE_World" type="Node3D"]',
    '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]',
    'environment = SubResource("Env_1")',
    '[node name="SunLight" type="DirectionalLight3D" parent="."]',
    'transform = Transform3D(0.866, -0.35, 0.35, 0, 0.707, 0.707, -0.5, -0.61, 0.61, 10, 18, 10)',
    'shadow_enabled = true',
    '[node name="ArenaFloor" type="MeshInstance3D" parent="."]',
    'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 4, -0.25, 4)',
    'mesh = SubResource("GroundMesh")',
    '[node name="Player" type="CharacterBody3D" parent="."]',
    'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 4, 1.2, 4)',
    'script = ExtResource("1")',
    '[node name="Mesh" type="MeshInstance3D" parent="Player"]',
    'mesh = SubResource("PlayerMesh")',
    '[node name="Camera3D" type="Camera3D" parent="Player"]',
    'transform = Transform3D(1, 0, 0, 0, 0.866, 0.5, 0, -0.5, 0.866, 0, 4.5, 7.5)',
    '[node name="PursuitHeli" type="Node3D" parent="."]',
    'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 9, 0)',
    'script = ExtResource("2")',
    '[node name="HeliBody" type="MeshInstance3D" parent="PursuitHeli"]',
    'mesh = SubResource("HeliMesh")',
    '[node name="SpotLight3D" type="SpotLight3D" parent="PursuitHeli"]',
    'light_energy = 6.0',
    'spot_range = 25.0'
]

for idx, (r, c) in enumerate(bp["objectives"]):
    nodes.append(f'[node name="NCM_CoverPillar_{idx}" type="MeshInstance3D" parent="."]')
    nodes.append(f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {r * 2.0}, 1.5, {c * 2.0})')
    nodes.append('mesh = SubResource("PillarMesh")')

with open(f"{PROJ}/scenes/main_arena.tscn", "w") as f:
    f.write("\n".join(nodes) + "\n")

# 6. Zip into /kaggle/working/TitanRAGE_Godot4.zip for 1-tap download into Godot 4 Editor!
zip_path = "/kaggle/working/TitanRAGE_Godot4.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(PROJ):
        for file in files:
            full = os.path.join(root, file)
            zf.write(full, os.path.relpath(full, PROJ))

print(f"READY! Download {zip_path} from Kaggle Output and open in https://godotengine.org !")

tok = UserSecretsClient().get_secret("GITHUB_TOKEN")
auto_sync.setup_auto_git("nike-eng", "Nemotron-NCM", tok)
auto_sync.sync_now("Exported Playable Godot 4 3D World (TitanRAGE_Godot4)")
