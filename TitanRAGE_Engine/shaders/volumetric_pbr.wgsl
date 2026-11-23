@vertex
fn vs_main(@builtin(vertex_index) vertexIndex : u32) -> @builtin(position) vec4<f32> {
    var pos = array<vec3<f32>, 3>(
        vec3<f32>(-1.0, -1.0, 0.0),
        vec3<f32>(1.0, -1.0, 0.0),
        vec3<f32>(0.0, 1.0, 0.0)
    );
    return vec4<f32>(pos[vertexIndex], 1.0);
}

@fragment
fn fs_main() -> @location(0) vec4<f32> {
    // Simplified PBR with rain wetness, roughness, and exponential height fog

    // Constants
    const PI : f32 = 3.141592653589793;
    const FOG_DENSITY : f32 = 0.05;
    const RAIN_WETNESS : f32 = 0.5;
    const ROUGHNESS : f32 = 0.3;

    // Simplified lighting parameters
    let lightDir = normalize(vec3<f32>(1.0, 1.0, 1.0));
    let viewDir = normalize(vec3<f32>(0.0, 0.0, -1.0));

    // Simplified albedo (diffuse color)
    let albedo = vec3<f32>(0.8, 0.8, 0.8);

    // Simplified normal (for simplicity, using the same for all pixels)
    let normal = normalize(vec3<f32>(0.0, 0.0, 1.0));

    // Diffuse term
    let diffuse = max(dot(normal, lightDir), 0.0);

    // Specular term (using Schlick's approximation)
    let spec = pow(max(dot(reflect(-lightDir, normal), viewDir), 0.0), 16.0);

    // Final color without fog
    let color = (albedo * diffuse + vec3<f32>(1.0, 1.0, 1.0) * spec) * (1.0 - RAIN_WETNESS);

    // Exponential height fog
    let depth = length(viewDir); // Simplified depth calculation
    let fogFactor = exp(-FOG_DENSITY * depth);
    color = mix(color, vec3<f32>(0.2, 0.2, 0.2), fogFactor);

    return vec4<f32>(color, 1.0);
}