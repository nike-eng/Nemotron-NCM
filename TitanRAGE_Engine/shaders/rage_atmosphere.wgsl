struct EnvUniforms { sun_dir: vec3<f32>, rain_wetness: f32, time: f32 };
@group(0) @binding(0) var<uniform> env: EnvUniforms;

@vertex
fn vs_main(@location(0) pos: vec3<f32>) -> @builtin(position) vec4<f32> {
    return vec4<f32>(pos, 1.0);
}

@fragment
fn fs_main(@location(0) world_pos: vec3<f32>, @location(1) normal: vec3<f32>) -> @location(0) vec4<f32> {
    let sun_amt = max(dot(normalize(normal), normalize(env.sun_dir)), 0.0);
    let puddle_roughness = mix(0.65, 0.08, env.rain_wetness);
    let sky_scatter = vec3<f32>(0.22, 0.48, 0.85) * (0.4 + 0.6 * sun_amt);
    let volumetric_fog = exp(-length(world_pos) * 0.012);
    let final_rgb = mix(sky_scatter, vec3<f32>(0.15, 0.17, 0.20) * (1.0 - puddle_roughness * 0.4) + sun_amt, volumetric_fog);
    return vec4<f32>(final_rgb, 1.0);
}
