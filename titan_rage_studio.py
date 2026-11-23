import os, json, math, urllib.request, gradio as gr
import plotly.graph_objects as go
from phase2_fusion import LiveNCMCoprocessor

BASE_DIR = "/kaggle/working/AI_Cyberdeck/TitanRAGE_Engine"
os.makedirs(f"{BASE_DIR}/animations", exist_ok=True)

def ask_frontier_coder(layer: str, prompt: str) -> str:
    or_key = os.environ.get("OPENROUTER_API_KEY", "")
    groq_key = os.environ.get("GROQ_API_KEY", "")

    if or_key:
        url = "https://openrouter.ai"
        key = or_key
        model = "openrouter/free"
    elif groq_key:
        url = "https://groq.com"
        key = groq_key
        model = "llama-3.3-70b-versatile"
    else:
        return "ERROR: Add OPENROUTER_API_KEY or GROQ_API_KEY in Kaggle Add-ons -> Secrets!"

    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": f"You are a senior Rockstar RAGE {layer} engine architect. Output ONLY clean, runnable {layer} code with zero markdown fences."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1200,
        "temperature": 0.1
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "TitanRAGE Studio"
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw_body = r.read().decode("utf-8")
        if not raw_body.strip():
            return "API returned empty response. Try again in 3 seconds."
        data = json.loads(raw_body)
        if "error" in data:
            return f"API Error: {data['error']}"
        txt = data["choices"]["message"]["content"]
        for fence in ["```rust", "```cpp", "```c++", "```lua", "```wgsl", "```"]:
            txt = txt.replace(fence, "")
        return txt.strip()
    except Exception as e:
        return f"Request Error: {e}"

def render_3d_viewport(seed, anim_name, sun, rain, px, pz, frame_idx=0):
    bp = LiveNCMCoprocessor().generate_arena_blueprint(seed_idx=int(seed))
    af = f"{BASE_DIR}/animations/{anim_name.lower()}.anim.json"
    if not os.path.exists(af):
        af = f"{BASE_DIR}/animations/tactical_sprint.anim.json"

    pelvis_y, lf_y, rf_y = 1.0, 0.0, 0.0
    if os.path.exists(af):
        frames = json.loads(open(af).read()).get("frames", [])
        if frames:
            fr = frames[int(frame_idx) % len(frames)]
            pelvis_y, lf_y, rf_y = fr["pelvis_y"], fr["left_foot_y"], fr["right_foot_y"]

    fig = go.Figure()

    # 1. NCM Spawn Pads (Cyan)
    if bp["spawns"]:
        sx, sz = zip(*bp["spawns"])
        fig.add_trace(go.Scatter3d(
            x=sx, y=sz, z=[0.05]*len(sx), mode="markers", name="NCM Spawn Pads",
            marker=dict(size=10, color="#00f0ff", symbol="circle")
        ))

    # 2. NCM Cover / Objective Pillars (Gold vertical lines + caps)
    for ox, oz in bp["objectives"]:
        fig.add_trace(go.Scatter3d(
            x=[ox, ox], y=[oz, oz], z=[0, 2.2], mode="lines+markers", showlegend=False,
            line=dict(color="#f59e0b", width=10), marker=dict(size=4, color="#fbbf24")
        ))

    # 3. Articulated Character Rig (Pelvis, Head, Left/Right IK Feet)
    fig.add_trace(go.Scatter3d(
        x=[px, px, px - 0.25, px, px + 0.25],
        y=[pz, pz, pz + (lf_y - 0.15), pz, pz + (rf_y - 0.15)],
        z=[pelvis_y + 0.65, pelvis_y, lf_y + 0.1, pelvis_y, rf_y + 0.1],
        mode="lines+markers", name=f"Player Rig ({anim_name})",
        line=dict(color="#38bdf8", width=7),
        marker=dict(size=[9, 7, 6, 7, 6], color=["#f8fafc", "#38bdf8", "#f43f5e", "#38bdf8", "#10b981"])
    ))

    bg_color = "#1e293b" if sun > 0.35 else "#090d16"
    fig.update_layout(
        title=f"TITAN-RAGE 3D VIEWPORT | Sector #{seed} | Rain: {rain:.2f} | Anim Frame: {int(frame_idx)}",
        paper_bgcolor=bg_color, font=dict(color="#e2e8f0"), height=460, margin=dict(l=0, r=0, t=40, b=0),
        scene=dict(
            xaxis=dict(range=[0, 9], backgroundcolor="#0f172a", gridcolor="#334155", title="X"),
            yaxis=dict(range=[0, 9], backgroundcolor="#0f172a", gridcolor="#334155", title="Z"),
            zaxis=dict(range=[0, 3], backgroundcolor="#0f172a", gridcolor="#334155", title="Height (Y)"),
            aspectmode="manual", aspectratio=dict(x=1.2, y=1.2, z=0.5)
        )
    )
    return fig

def bake_anim(name, spd, lift, seed, sun, rain, px, pz, frame_idx):
    safe = "".join(c for c in name if c.isalnum() or c == "_") or "CustomAnim"
    out = f"{BASE_DIR}/animations/{safe.lower()}.anim.json"
    frames = [{"t": round(i/60, 3), "pelvis_y": round(1.0 + abs(math.sin(i/60*6.283*spd))*0.09, 3),
               "left_foot_y": round(max(0.0, math.sin(i/60*6.283*spd)*lift), 3),
               "right_foot_y": round(max(0.0, -math.sin(i/60*6.283*spd)*lift), 3)} for i in range(60)]
    open(out, "w").write(json.dumps({"name": safe, "fps": 60, "frames": frames}))
    return f"Baked C++20/IK Clip '{safe}' (60 FPS) -> {out}", render_3d_viewport(seed, safe, sun, rain, px, pz, frame_idx)

with gr.Blocks(title="TitanRAGE Studio 3D") as studio:
    gr.Markdown("# 🎮 TITAN-RAGE STUDIO 3D — VIEWPORT, IK ANIMATOR & CLOUD CODER")
    with gr.Row():
        with gr.Column(scale=1):
            seed = gr.Slider(minimum=0, maximum=1999, value=99, step=1, label="NCM World Sector Seed")
            px = gr.Slider(minimum=0, maximum=8, value=4, step=0.5, label="Player Rig X")
            pz = gr.Slider(minimum=0, maximum=8, value=4, step=0.5, label="Player Rig Z")
            sun = gr.Slider(minimum=0.0, maximum=1.0, value=0.8, step=0.05, label="Sun Elevation")
            rain = gr.Slider(minimum=0.0, maximum=1.0, value=0.6, step=0.05, label="RAGE Rain Wetness")
            frame_sl = gr.Slider(minimum=0, maximum=59, value=15, step=1, label="Scrub Animation Timeline (Frame 0–59)")
            aname = gr.Textbox(label="Custom Animation Name", value="Tactical_Sprint")
            aspd = gr.Slider(minimum=0.5, maximum=5.0, value=2.4, step=0.1, label="Cycle Speed (Hz)")
            alift = gr.Slider(minimum=0.05, maximum=0.8, value=0.35, step=0.05, label="Stride Lift Height")
            abtn = gr.Button("Bake & Preview Animation", variant="primary")
            astat = gr.Textbox(label="Engine Status", interactive=False)
        with gr.Column(scale=2):
            view = gr.Plot(value=render_3d_viewport(99, "Tactical_Sprint", 0.8, 0.6, 4.0, 4.0, 15))
            layer = gr.Dropdown(["Rust Core", "C++20 Physics", "WGSL Shader", "Lua 5.4 Mission"], value="Lua 5.4 Mission", label="Engine Layer")
            prompt = gr.Textbox(label="Frontier Free Coder Prompt", value="Write a helicopter pursuit & spotlight tracking AI script in Lua 5.4.")
            gbtn = gr.Button("Generate via Free Frontier Coder")
            code_out = gr.Code(label="Generated Code", language="cpp")

    ctrls = [seed, aname, sun, rain, px, pz, frame_sl]
    for c in [seed, px, pz, sun, rain, frame_sl]:
        c.change(render_3d_viewport, ctrls, view)
    abtn.click(bake_anim, [aname, aspd, alift, seed, sun, rain, px, pz, frame_sl], [astat, view])
    gbtn.click(ask_frontier_coder, [layer, prompt], code_out)

studio.launch(share=True)
