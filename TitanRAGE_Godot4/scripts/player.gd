extends CharacterBody3D

@export_group("Movement Settings")
@export var walk_speed: float = 5.0
@export var sprint_speed: float = 8.0
@export var jump_velocity: float = 4.5
@export var acceleration: float = 10.0
@export var friction: float = 12.0

@export_group("Procedural Bobbing")
@export var bob_freq: float = 2.4
@export var bob_amp: float = 0.08
@export var smooth_speed: float = 10.0

@onready var mesh: MeshInstance3D = $Mesh

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")
var bob_time: float = 0.0
var default_mesh_pos: Vector3

func _ready() -> void:
	default_mesh_pos = mesh.position

func _physics_process(delta: float) -> void:
	# Apply Gravity
	if not is_on_floor():
		velocity.y -= gravity * delta

	# Handle Jump
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity

	# Handle Sprinting
	var current_speed: float = sprint_speed if Input.is_action_pressed("shift") else walk_speed

	# Get Input Direction (WASD / Joystick)
	var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	# Movement Logic (Acceleration/Friction)
	if direction:
		velocity.x = lerp(velocity.x, direction.x * current_speed, acceleration * delta)
		velocity.z = lerp(velocity.z, direction.z * current_speed, acceleration * delta)
	else:
		velocity.x = lerp(velocity.x, 0.0, friction * delta)
		velocity.z = lerp(velocity.z, 0.0, friction * delta)

	move_and_slide()
	_apply_bobbing(delta)

func _apply_bobbing(delta: float) -> void:
	# Only bob if moving on floor
	var is_moving: bool = velocity.length() > 0.1 and is_on_floor()
	
	if is_moving:
		# Increment time based on speed to sync bob with movement
		bob_time += delta * velocity.length()
		
		var target_pos_y: float = default_mesh_pos.y + sin(bob_time * bob_freq) * bob_amp
		var target_pos_x: float = default_mesh_pos.x + cos(bob_time * bob_freq * 0.5) * bob_amp
		
		mesh.position.y = lerp(mesh.position.y, target_pos_y, smooth_speed * delta)
		mesh.position.x = lerp(mesh.position.x, target_pos_x, smooth_speed * delta)
	else:
		# Reset bobbing smoothly when idle
		bob_time = 0.0
		mesh.position = mesh.position.lerp(default_mesh_pos, smooth_speed * delta)