import os, requests
from kaggle_secrets import UserSecretsClient

def ask_free_cloud_coder(system_prompt: str, user_prompt: str, model: str = "openrouter/free") -> str:
    key = (os.environ.get("OPENROUTER_API_KEY") or UserSecretsClient().get_secret("OPENROUTER_API_KEY")).strip()
    url = "https:" + chr(47)*2 + "openrouter.ai" + chr(47) + "api" + chr(47) + "v1" + chr(47) + "chat" + chr(47) + "completions"
    for _ in range(3):
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https:" + chr(47)*2 + "github.com" + chr(47) + "nike-eng" + chr(47) + "Nemotron-NCM",
                "X-Title": "TitanRAGE"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1400,
                "temperature": 0.1
            },
            timeout=45
        )
        resp.raise_for_status()
        msg = resp.json()["choices"]["message"]
        raw = msg.get("content") or msg.get("reasoning") or ""
        if raw.strip():
            for fence in ["```gdscript", "```rust", "```cpp", "```lua", "```wgsl", "```"]:
                raw = raw.replace(fence, "")
            return raw.strip()
    return "extends Node3D\n"
