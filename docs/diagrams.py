# Generates the README diagrams, each in a light and a dark version:
#   python3 docs/diagrams.py docs   ->  docs/{cluster,network,secrets,gitops}-{light,dark}.svg
# Kept generic on purpose: no addresses, hostnames or secret values.
import sys, html

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs"
W = 960
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
  "light": dict(bg="#ffffff", card="#f6f8fa", border="#d0d7de", text="#1f2328", muted="#656d76",
                blue="#0969da", blue_s="#ddf4ff", green="#1a7f37", green_s="#dafbe1",
                purple="#8250df", purple_s="#fbefff", amber="#9a6700", amber_s="#fff8c5",
                orange="#bc4c00", orange_s="#fff1e5", teal="#1b7c83", teal_s="#d8f3f6"),
  "dark":  dict(bg="#0d1117", card="#161b22", border="#30363d", text="#e6edf3", muted="#8d96a0",
                blue="#4493f8", blue_s="#121d2f", green="#3fb950", green_s="#12261e",
                purple="#ab7df8", purple_s="#231a33", amber="#d29922", amber_s="#272115",
                orange="#db6d28", orange_s="#2a1a10", teal="#39c5cf", teal_s="#0f2629"),
}

def esc(s): return html.escape(s, quote=True)


class Svg:
    def __init__(self, t, h, label):
        self.t, self.h, self.p = t, h, []
        self.p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label)}">')
        self.p.append(f'<title>{esc(label)}</title>')
        m = t["muted"]
        self.p.append(f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{m}"/></marker></defs>')
        self.p.append(f'<rect width="{W}" height="{h}" rx="14" fill="{t["bg"]}"/>')

    def text(self, x, y, s, size=12, color="text", weight=None, mono=False, anchor=None, spacing=None, italic=False):
        a = [f'x="{x:.0f}"', f'y="{y:.0f}"', f'font-family="{MONO if mono else FONT}"', f'font-size="{size}"', f'fill="{self.t.get(color, color)}"']
        if weight: a.append(f'font-weight="{weight}"')
        if anchor: a.append(f'text-anchor="{anchor}"')
        if spacing: a.append(f'letter-spacing="{spacing}"')
        if italic: a.append('font-style="italic"')
        self.p.append(f'<text {" ".join(a)}>{esc(s)}</text>')

    def label(self, x, y, s):  # small caps section label
        self.text(x, y, s.upper(), size=11, color="muted", weight=600, spacing=1.4)

    def rect(self, x, y, w, h, fill="card", stroke="border", rx=10, dash=None, sw=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{self.t.get(fill, fill)}" stroke="{self.t.get(stroke, stroke)}" stroke-width="{sw}"{d}/>')

    def card(self, x, y, w, h, title, subs=(), accent=None, tsize=14, mono_title=False):
        self.rect(x, y, w, h)
        tx = x + 16
        if accent:
            self.p.append(f'<rect x="{x:.0f}" y="{y+12:.0f}" width="3" height="{h-24:.0f}" rx="1.5" fill="{self.t[accent]}"/>')
        self.text(tx, y + 23, title, size=tsize, weight=600, mono=mono_title)
        for i, s in enumerate(subs):
            self.text(tx, y + 41 + i * 16, s, size=11.5, color="muted")

    def chip(self, x, y, s, color="blue"):
        w = 7.0 * len(s) + 18
        self.p.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="22" rx="11" fill="{self.t[color + "_s"]}"/>')
        self.text(x + w / 2, y + 15, s, size=11.5, color=color, mono=True, anchor="middle")
        return w

    def arrow(self, pts, note=None, nx=None, ny=None, dash=False, both=False):
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        extra = ' stroke-dasharray="5 4"' if dash else ""
        start = ' marker-start="url(#a)"' if both else ""
        self.p.append(f'<path d="{d}" fill="none" stroke="{self.t["muted"]}" stroke-width="1.5"{extra}{start} marker-end="url(#a)"/>')
        if note:
            self.text(nx, ny, note, size=11, color="muted", anchor="middle", italic=True)

    def save(self, name, theme):
        self.p.append("</svg>")
        open(f"{OUT}/{name}-{theme}.svg", "w").write("\n".join(self.p) + "\n")


def grid(s, x0, y0, cols, items, accent, w_total=W - 48, gap=10, h=58):
    for i, (title, sub) in enumerate(items):
        r, c = divmod(i, cols)
        n = min(cols, len(items) - r * cols)      # cards in this row; a short last row stretches
        w = (w_total - gap * (n - 1)) / n
        s.card(x0 + c * (w + gap), y0 + r * (h + gap), w, h, title, [sub], accent=accent)
    rows = (len(items) + cols - 1) // cols
    return y0 + rows * h + (rows - 1) * gap


# ---------------------------------------------------------------- cluster
PLATFORM = [
    ("Argo CD", "syncs every app folder from git"),
    ("Forgejo", "git, packages and CI; source of truth"),
    ("Authelia", "one sign-in + 2FA, also for kubectl"),
    ("External Secrets", "Vault secrets become k8s Secrets"),
    ("Longhorn", "replicated volumes, nightly backups"),
    ("CloudNativePG", "Postgres for Forgejo"),
    ("VictoriaMetrics", "metrics, Grafana, alerts"),
    ("Headlamp", "cluster UI, signs in with Authelia"),
]
APPS = [
    ("Ente Photos", "photo backup for family + friends"),
    ("Ente staging", "copy of prod to test upgrades on"),
    ("ente-admin", "admin portal I built for Ente"),
    ("ente-notify", "the emails Ente doesn't send"),
    ("Plex", "iGPU transcoding, viewing stats"),
    ("Actual Budget", "household budget, OpenID sign-in"),
    ("Homepage", "one dashboard for everything"),
    ("Uptime Kuma", "uptime checks + outside heartbeat"),
    ("Renovate", "a pull request for every new image"),
    ("Forgejo runner", "CI builds with rootless BuildKit"),
    ("Intel GPU plugin", "offers each node's iGPU to pods"),
]
PROJECTS = [
    ("temupuffer", "an object-storage search database"),
    ("temupuffer-search", "500k arXiv papers on top of it"),
    ("Napkin Math UI", "latency + cost calculator"),
]
STORAGE = [
    ("Longhorn", "node disks, replicated across nodes"),
    ("NFS from the NAS", "photo objects and the media library"),
    ("Backups", "volumes nightly · VMs · ZFS replication"),
]

def cluster(t):
    s = Svg(t, 790, "The k3s cluster: three nodes, the platform installed by Ansible, the apps Argo CD deploys, my projects, and storage")
    x0 = 24
    s.label(x0, 36, "Nodes")
    s.text(W - 24, 36, "every node is a server (embedded etcd) and runs workloads", size=11.5, color="muted", anchor="end")
    nw = (W - 48 - 20) / 3
    for i in range(3):
        s.card(x0 + i * (nw + 10), 48, nw, 74, f"k3s-prod0{i+1}", [f"VM on Proxmox host {i+1} · 4 vCPU · 10 GB", "Intel iGPU passed through · Traefik"], accent="teal", mono_title=True)
    y = 154
    s.label(x0, y, "Platform")
    s.text(W - 24, y, "installed by Ansible, so nothing depends on what it fixes", size=11.5, color="muted", anchor="end")
    y = grid(s, x0, y + 12, 4, PLATFORM, "blue") + 32
    s.label(x0, y, "Apps")
    s.text(W - 24, y, "one folder each in git, deployed by Argo CD", size=11.5, color="muted", anchor="end")
    y = grid(s, x0, y + 12, 4, APPS, "green") + 32
    s.label(x0, y, "My projects")
    s.text(W - 24, y, "built here, public on GitHub", size=11.5, color="muted", anchor="end")
    y = grid(s, x0, y + 12, 3, PROJECTS, "purple") + 32
    s.label(x0, y, "Storage")
    s.text(W - 24, y, "pods are disposable; data lives here", size=11.5, color="muted", anchor="end")
    grid(s, x0, y + 12, 3, STORAGE, "amber")
    return s


# ---------------------------------------------------------------- network
def network(t):
    s = Svg(t, 470, "Network: devices reach the lab over WireGuard through OPNsense, which filters per device group, load-balances with HAProxy and answers DNS; servers, storage and home are separate networks")
    cx, cw = 24, 230          # clients
    fx, fw = 314, 340         # firewall
    zx, zw = 718, 218         # zones
    s.label(cx, 36, "Who connects")
    s.label(fx, 36, "Firewall")
    s.label(zx, 36, "Networks")
    clients = [
        ("My devices", ["WireGuard, split tunnel", "full access"], "orange"),
        ("Family devices", ["WireGuard, HTTPS + DNS only", "everything else blocked + logged"], "orange"),
        ("The internet", ["only WireGuard and Plex", "are open from outside"], None),
    ]
    ch, cg = 74, 64
    for i, (ti, su, ac) in enumerate(clients):
        s.card(cx, 52 + i * (ch + cg), cw, ch, ti, su, accent=ac)

    # OPNsense box
    s.rect(fx, 52, fw, 350, fill="orange_s", stroke="orange", rx=12)
    s.text(fx + 18, 78, "OPNsense", size=15, weight=600)
    s.text(fx + fw - 18, 78, "router + firewall", size=11.5, color="muted", anchor="end")
    rows = [
        ("WireGuard", ["one tunnel, rules per device group"]),
        ("Firewall rules", ["each network kept apart"]),
        ("HAProxy", ["one virtual IP: k3s API on all 3 nodes,", "HTTPS ingress, Vault, Plex"]),
        ("DNS", ["AdGuard filters, Unbound names the lab"]),
    ]
    ry = 92
    rh = [62, 62, 78, 62]
    for (ti, su), h in zip(rows, rh):
        s.card(fx + 14, ry, fw - 28, h, ti, su)
        ry += h + 12

    zones = [
        ("Servers", ["3 Proxmox hosts", "k3s VMs + the Vault VM"], "teal"),
        ("Storage", ["NAS: NFS for photos,", "media and backups"], "amber"),
        ("Home", ["everyday devices"], None),
    ]
    zy = [52, 186, 320]
    for (ti, su, ac), y in zip(zones, zy):
        s.card(zx, y, zw, 82 if len(su) > 1 else 66, ti, su, accent=ac)

    # arrows: clients -> WireGuard row
    wg_y = 92 + 31
    for i in range(2):
        y = 52 + i * (ch + cg) + ch / 2
        s.arrow([(cx + cw, y), (cx + cw + 30, y), (cx + cw + 30, wg_y), (fx + 14, wg_y)])
    # internet -> HAProxy (Plex port forward)
    iy = 52 + 2 * (ch + cg) + ch / 2
    hp_y = 92 + 62 + 12 + 62 + 12 + 39
    s.arrow([(cx + cw, iy), (cx + cw + 30, iy), (cx + cw + 30, hp_y), (fx + 14, hp_y)])
    s.text(cx + cw + 4, iy + 16, "Plex", size=11, color="muted", italic=True)
    # HAProxy -> servers
    s.arrow([(fx + fw - 14, hp_y), (fx + fw + 32, hp_y), (fx + fw + 32, 93), (zx, 93)])
    # servers -> storage
    s.arrow([(zx + zw / 2, 134), (zx + zw / 2, 186)], note="NFS, through the firewall", nx=zx + zw / 2, ny=166)
    s.text(W / 2, 444, "Every web UI is behind Authelia sign-in with 2FA, even inside the tunnel.", size=12, color="muted", anchor="middle")
    return s


# ---------------------------------------------------------------- secrets
APP_PATHS = ["actual", "argocd", "authelia", "ente", "ente-admin", "forgejo", "headlamp",
             "homepage", "media", "renovate", "uptime"]

def secrets(t):
    s = Svg(t, 470, "Secrets: Vault on its own VM holds every secret; External Secrets, Ansible and Terraform read them at run time; nothing is in git")
    vx, vw = 24, 250
    px, pw = 318, 300
    ox, ow = 662, 274
    s.label(vx, 36, "Vault")
    s.label(px, 36, "Paths (KV v2)")
    s.label(ox, 36, "Who reads them")

    s.rect(vx, 52, vw, 320, fill="amber_s", stroke="amber", rx=12)
    s.text(vx + 18, 80, "HashiCorp Vault", size=15, weight=600)
    s.text(vx + 18, 98, "its own VM, outside the cluster", size=11.5, color="muted")
    facts = [("Raft storage", "integrated, no extra database"), ("TLS + audit log", "every request recorded"),
             ("Nightly snapshots", "plus the VM is replicated"), ("Unseal: 3 of 5 keys", "kept offline, never in git")]
    for i, (a, b) in enumerate(facts):
        s.card(vx + 14, 114 + i * 63, vw - 28, 53, a, [b], tsize=13)

    # path cards
    s.rect(px, 52, pw, 196)
    s.text(px + 16, 76, "secret/k8s/<app>", size=13.5, weight=600, mono=True)
    s.text(px + 16, 94, "one folder per app", size=11.5, color="muted")
    cx, cy = px + 16, 108
    for name in APP_PATHS:
        w = 7.0 * len(name) + 18
        if cx + w > px + pw - 12:
            cx, cy = px + 16, cy + 30
        s.chip(cx, cy, name, "amber")
        cx += w + 6
    s.card(px, 262, pw, 50, "secret/k3s/cluster", [], mono_title=True, tsize=13.5)
    s.text(px + pw - 16, 285, "cluster join token", size=11.5, color="muted", anchor="end")
    s.card(px, 322, pw, 50, "secret/proxmox/terraform", [], mono_title=True, tsize=13.5)
    s.text(px + pw - 16, 345, "API token", size=11.5, color="muted", anchor="end")

    # readers
    s.card(ox, 52, ow, 152, "External Secrets", ["logs in with Kubernetes auth:", "no Vault token stored in the cluster", "read-only, and only on k8s/*", "29 secrets in 16 namespaces,", "refreshed into k8s Secrets hourly"], accent="blue")
    s.card(ox, 236, ow, 60, "Ansible", ["looks secrets up at run time"], accent="blue")
    s.card(ox, 312, ow, 60, "Terraform", ["gets its token from a wrapper script"], accent="blue")
    s.arrow([(px + pw, 150), (ox, 150)])
    s.arrow([(px + pw, 287), (ox, 266)])
    s.arrow([(px + pw, 347), (ox, 342)])
    # vault -> paths
    s.arrow([(vx + vw, 150), (px, 150)])

    s.text(W / 2, 408, "No secret is committed to any repo, public or private.", size=12.5, color="text", anchor="middle", weight=600)
    s.text(W / 2, 428, "New values go straight into Vault; apps restart when a credential's revision annotation changes.", size=12, color="muted", anchor="middle")
    return s


# ---------------------------------------------------------------- gitops
def gitops(t):
    s = Svg(t, 440, "Getting changes in: push to Forgejo, Argo CD syncs the cluster; Renovate proposes image updates that are mirrored first; Ansible installs the platform; GitHub gets a mirror")
    cols = [(24, 170), (234, 210), (484, 210), (734, 202)]
    my, mh = 168, 92
    mains = [("Laptop", ["edit, preview, push", "a branch + pull request"], None),
             ("Forgejo", ["in the cluster, the source", "of truth; CI on Actions"], "blue"),
             ("Argo CD", ["one app per folder,", "prunes + self-heals"], "blue"),
             ("k3s", ["apps run", "what git says"], "teal")]
    for (x, w), (ti, su, ac) in zip(cols, mains):
        s.card(x, my, w, mh, ti, su, accent=ac, tsize=15)
    cy = my + mh / 2
    s.arrow([(24 + 170, cy), (234, cy)], note="push", nx=214, ny=cy - 8)
    s.arrow([(234 + 210, cy), (484, cy)], note="merge", nx=464, ny=cy - 8)
    s.arrow([(484 + 210, cy), (734, cy)], note="sync", nx=714, ny=cy - 8)

    s.label(24, 36, "Updates")
    s.card(234, 52, 210, 70, "Renovate", ["a pull request per new image"], accent="green")
    s.card(484, 52, 452, 70, "Image mirror", ["a workflow copies the new image into Forgejo's registry", "before the merge; nodes pull from there first"], accent="green")
    s.arrow([(339, 122), (339, my)], note="opens PR", nx=375, ny=148)
    s.arrow([(444, 87), (484, 87)])
    s.arrow([(835, 122), (835, my)], dash=True, note="pulls", nx=860, ny=148)

    s.label(24, 304, "Around it")
    s.card(234, 320, 210, 70, "GitHub", ["push mirror of public repos"])
    s.arrow([(339, my + mh), (339, 320)], dash=True, note="mirror", nx=368, ny=296)
    s.card(484, 320, 452, 70, "Ansible", ["installs k3s + the platform: --check --diff first,", "restarts one node at a time"], accent="blue")
    s.arrow([(835, 320), (835, my + mh)], note="platform", nx=866, ny=296)
    s.card(24, 320, 170, 70, "Terraform", ["the VMs on Proxmox"])
    s.text(W / 2, 422, "Every change is a commit, so every change can be reviewed and reverted.", size=12, color="muted", anchor="middle")
    return s


for theme, t in THEMES.items():
    for name, fn in [("cluster", cluster), ("network", network), ("secrets", secrets), ("gitops", gitops)]:
        fn(t).save(name, theme)
