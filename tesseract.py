"""Rotating tesseract (4D hypercube) as a self-contained SVG animation (SMIL, no scripts)."""
import itertools, math

VERTS = list(itertools.product((-1, 1), repeat=4))
EDGES = [(i, j) for i in range(16) for j in range(i + 1, 16)
         if sum(a != b for a, b in zip(VERTS[i], VERTS[j])) == 1]
W_EDGES = [e for e in EDGES if VERTS[e[0]][3] != VERTS[e[1]][3]]   # 8 connectors between the two cubes
CUBE_EDGES = [e for e in EDGES if e not in W_EDGES]                # 24 cube edges


def rot(p, i, j, a):
    c, s = math.cos(a), math.sin(a)
    q = list(p)
    q[i], q[j] = p[i] * c - p[j] * s, p[i] * s + p[j] * c
    return q


def project(theta, cx, cy, scale):
    pts = []
    for v in VERTS:
        p = rot(v, 0, 3, theta)        # X-W: the 4D turn that makes the inner cube pass through the outer
        p = rot(p, 1, 2, 2 * theta)    # Y-Z: ordinary 3D spin
        p = rot(p, 0, 1, theta)        # X-Y: slow roll
        k = 1 / (2.6 - p[3])           # 4D -> 3D
        x, y, z = p[0] * k, p[1] * k, p[2] * k
        f = 1 / (3.2 - z)              # 3D -> 2D
        pts.append((cx + x * f * scale * 3.2, cy + y * f * scale * 3.2))
    return pts


def frames(edges, cx, cy, scale, n):
    out = []
    for f in range(n + 1):  # last frame == first, so the loop is seamless
        pts = project(2 * math.pi * (f % n) / n, cx, cy, scale)
        out.append("".join(f"M{pts[a][0]:.1f} {pts[a][1]:.1f}L{pts[b][0]:.1f} {pts[b][1]:.1f}" for a, b in edges))
    return ";".join(out)


def svg(cx, cy, scale=30, n=60, dur=16, c_cube="#d4a843", c_w="#3ddc97", blur=1.6, wc=1.4):
    return (
        f'<defs><filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
        '<feGaussianBlur stdDeviation="{blur}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        f'<g filter="url(#glow)" fill="none" stroke-linecap="round">'
        f'<path stroke="{c_cube}" stroke-width="{wc}" d="{frames(CUBE_EDGES, cx, cy, scale, n).split(";")[0]}"><animate attributeName="d" dur="{dur}s" repeatCount="indefinite" '
        f'values="{frames(CUBE_EDGES, cx, cy, scale, n)}"/></path>'
        f'<path stroke="{c_w}" stroke-width="{wc * .8:.2f}" d="{frames(W_EDGES, cx, cy, scale, n).split(";")[0]}"><animate attributeName="d" dur="{dur}s" repeatCount="indefinite" '
        f'values="{frames(W_EDGES, cx, cy, scale, n)}"/></path></g>')
