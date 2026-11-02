"""Validate the shared package and rebuild the standalone skill ZIP (no network)."""
import hashlib
import json
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
plugin = root / "plugins/smetchik"
skill = plugin / "skills/smetchik"
source = json.loads((root / "SOURCE.json").read_text(encoding="utf-8"))
for rel, digest in source["files"].items():
    assert hashlib.sha256((skill / rel).read_bytes()).hexdigest() == digest, rel
for rel in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
    manifest = json.loads((plugin / rel).read_text(encoding="utf-8"))
    assert manifest["name"] == "smetchik"
    assert manifest["version"] == "1.1.0"
for rel in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
    catalog = json.loads((root / rel).read_text(encoding="utf-8"))
    assert catalog["name"] == "smetchik-client"
    assert len(catalog["plugins"]) == 1
for rel in ("mcp.json", ".mcp.json"):
    servers = json.loads((plugin / rel).read_text(encoding="utf-8"))["mcpServers"]
    assert list(servers) == ["smetchik"]
    assert servers["smetchik"]["url"] == "https://smeta.nakasse.kz/mcp"
out = root / "dist/smetchik-client.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for rel in source["files"]:
        archive.write(skill / rel, "smetchik/" + rel)
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
print("PASS: shared skill hashes, manifests, MCP URLs, ZIP")
