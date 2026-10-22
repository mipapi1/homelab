# Generates stack-light.svg and stack-dark.svg: python3 docs/stack.py docs
import sys, html
out = sys.argv[1]
THEMES = {
  "light": dict(bg="#ffffff", card="#f6f8fa", border="#d0d7de", text="#1f2328", muted="#656d76", accent="#0969da", chip="#ddf4ff"),
  "dark":  dict(bg="#0d1117", card="#161b22", border="#30363d", text="#e6edf3", muted="#8d96a0", accent="#4493f8", chip="#121d2f"),
}
W = 880
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
# (layer label, [(title, subtitle, repo)])  top to bottom
ROWS = [
  ("APPS", [("Plex · Uptime Kuma · Homepage · Renovate", "one folder per app · Argo CD syncs from git · images mirrored", "k3s-homelab-apps")]),
  ("PLATFORM", [("k3s · Argo CD · Forgejo · Authelia", "Longhorn · External Secrets · VictoriaMetrics · Headlamp", "ansible-k3s-homelab"),
                ("Vault", "Raft · TLS · nightly snapshots", "ansible-vault-raft")]),
  ("VIRTUAL MACHINES", [("3 × k3s nodes", "HA control plane · iGPU passthrough", "terraform-proxmox-vm"),
                        ("Vault VM", "ZFS-replicated to every host", "terraform-proxmox-vm")]),
  ("HARDWARE", [("Proxmox VE 9 · 3 × Intel N100/N150 mini PCs", "ZFS replication · NAS over NFS · OPNsense firewall · WireGuard VPN", "~ Set up by hand. Everything above it is code.")]),
]
X0, LABEL_W, GAP, ROW_H, ROW_GAP, TOP = 28, 150, 12, 100, 14, 28
H = TOP*2 + len(ROWS)*ROW_H + (len(ROWS)-1)*ROW_GAP

def esc(s): return html.escape(s, quote=True)

def card(t, x, y, w, title, sub, repo):
    s = [f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{ROW_H}" rx="10" fill="{t["card"]}" stroke="{t["border"]}"/>']
    s.append(f'<text x="{x+18:.0f}" y="{y+30}" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["text"]}">{esc(title)}</text>')
    s.append(f'<text x="{x+18:.0f}" y="{y+51}" font-family="{FONT}" font-size="12.5" fill="{t["muted"]}">{esc(sub)}</text>')
    if repo and repo.startswith("~"):
        s.append(f'<text x="{x+18:.0f}" y="{y+80}" font-family="{FONT}" font-size="12" fill="{t["muted"]}" opacity="0.8">{esc(repo[1:].strip())}</text>')
    elif repo:
        cw = 7.2*len(repo) + 22
        s.append(f'<rect x="{x+16:.0f}" y="{y+64}" width="{cw:.0f}" height="22" rx="11" fill="{t["chip"]}"/>')
        s.append(f'<text x="{x+16+cw/2:.0f}" y="{y+79}" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="{t["accent"]}">{esc(repo)}</text>')
    return s

for name, t in THEMES.items():
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Homelab stack: hardware, virtual machines, platform, apps">',
         f'<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>']
    for i, (label, cards) in enumerate(ROWS):
        y = TOP + i*(ROW_H+ROW_GAP)
        p.append(f'<text x="{X0}" y="{y+ROW_H/2+4}" font-family="{FONT}" font-size="11" font-weight="600" letter-spacing="1.4" fill="{t["muted"]}">{label}</text>')
        x = X0 + LABEL_W
        avail = W - x - X0
        # first card takes the rest when there are two
        widths = [avail] if len(cards) == 1 else [avail*0.66 - GAP/2, avail*0.34 - GAP/2]
        for (title, sub, repo), w in zip(cards, widths):
            p += card(t, x, y, w, title, sub, repo)
            x += w + GAP
    p.append('</svg>')
    open(f"{out}/stack-{name}.svg", "w").write("\n".join(p) + "\n")
