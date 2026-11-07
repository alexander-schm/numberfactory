"""
Render the Zahlenwerk machine sprites with Blender (Cycles, transparent background).

Usage:
  /Applications/Blender.app/Contents/MacOS/Blender -b -P blender/render_sprites.py -- <out_dir>

Scale convention: 1 Blender unit = 50 game px. Sprites are rendered at 2x (100 px per unit).
Every sprite is framed so that the world origin (the top-centre of the machine) lands
exactly in the image centre – the game draws each sprite centred on its node position.
"""
import bpy, bmesh, math, os, sys

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT, exist_ok=True)
PX_PER_UNIT = 100           # 2x of 50 game px per unit
TILT = math.radians(37)     # camera tilt from vertical; cos(37°) ≈ 0.8 matches the game's ellipses

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, 1.0)

# ---------------------------------------------------------------- scene setup
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'; prefs.get_devices()
        for d in prefs.devices: d.use = True
        sc.cycles.device = 'GPU'
    except Exception:
        sc.cycles.device = 'CPU'
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    world = bpy.data.worlds.new('w'); sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']; bg.inputs[0].default_value = srgb('#fbf8ee'); bg.inputs[1].default_value = 0.55
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 1.5; sun.angle = math.radians(30)
    so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(38), math.radians(-10), math.radians(-35))
    return sc

MATS = {}
def mat(hexcol, rough=0.55):
    key = (hexcol, rough)
    if key in MATS: return MATS[key]
    m = bpy.data.materials.new(hexcol)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = srgb(hexcol)
    p.inputs['Roughness'].default_value = rough
    MATS[key] = m
    return m

def finish(obj, material, outline=None, bevel=0.02, thick=0.022):
    obj.data.materials.append(material)
    if bevel:
        b = obj.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 3; b.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = obj
    for p in obj.data.polygons: p.use_smooth = True
    try: obj.data.shade_auto_smooth(angle=math.radians(40))
    except Exception: pass
    # (`outline`/`thick` are kept for call-site readability; the actual outline is drawn in
    #  post-processing around the whole silhouette, see add_outline())
    return obj

def cyl(r, depth, z_top, material, outline=None, verts=64, bevel=0.03, x=0, y=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=(x, y, z_top - depth / 2))
    return finish(bpy.context.object, material, outline, bevel)

def box(sx, sy, sz, loc, material, outline=None, bevel=0.03, rot=(0, 0, 0), thick=0.022):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, material, outline, bevel, thick)

def torus(R, r, z, material, x=0, y=0):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=(x, y, z), major_segments=64, minor_segments=12)
    return finish(bpy.context.object, material, None, 0)

def ground(z):
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, z))
    g = bpy.context.object; g.is_shadow_catcher = True
    g.data.materials.append(mat('#ffffff'))
    return g

def add_outline(path, hexcol, radius):
    """Draw an ink outline around the solid silhouette (ignores the soft drop shadow)."""
    import numpy as np
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
    a = px.reshape(h, w, 4)
    solid = np.clip((a[..., 3] - 0.85) * 8.0, 0, 1)         # object pixels; the soft shadow stays below this
    dil = solid.copy()
    for dy in range(-radius - 1, radius + 2):
        for dx in range(-radius - 1, radius + 2):
            d = math.hypot(dx, dy)
            if d > radius + 1: continue
            wgt = 1.0 if d <= radius else radius + 1 - d     # anti-aliased rim
            dil = np.maximum(dil, wgt * np.roll(np.roll(solid, dy, 0), dx, 1))
    c = [int(hexcol.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4)]
    if img.colorspace_settings.name != 'sRGB' or img.is_float:
        pass
    # clean the shadow: drop the faint ambient haze of the shadow catcher and fade towards the frame border
    alpha = a[..., 3]
    shadow = 1 - solid
    yy, xx = np.mgrid[0:h, 0:w]
    border = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / (0.12 * min(w, h))
    fade = np.clip(border, 0, 1) ** 2
    cleaned = np.clip((alpha - 0.05) / 0.95, 0, 1) * fade
    a[..., 3] = solid * alpha + shadow * np.minimum(alpha, cleaned)
    at = a[..., 3:4]; ab = dil[..., None]
    A = at + ab * (1 - at)
    col = np.array(c, dtype=np.float32)
    rgb = (a[..., :3] * at + col * ab * (1 - at)) / np.maximum(A, 1e-6)
    out = np.concatenate([rgb, A], axis=2).astype(np.float32)
    img.pixels.foreach_set(out.ravel())
    img.filepath_raw = path; img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)

def render(name, frame_w, frame_h, ink='#3a6b65', ink_px=4):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'
    cam.ortho_scale = max(frame_w, frame_h)
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
    d = 20
    co.location = (0, -d * math.sin(TILT), d * math.cos(TILT))
    co.rotation_euler = (TILT, 0, 0)
    sc.render.resolution_x = round(frame_w * PX_PER_UNIT)
    sc.render.resolution_y = round(frame_h * PX_PER_UNIT)
    sc.render.resolution_percentage = 100
    cam.sensor_fit = 'HORIZONTAL' if frame_w >= frame_h else 'VERTICAL'
    sc.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    if ink: add_outline(sc.render.filepath, ink, ink_px)
    print('rendered', sc.render.filepath)

# ---------------------------------------------------------------- palette
INK = '#3a6b65'; INK_WARM = '#6b6250'
MINT_TOP = '#eef5f3'; MINT_SIDE = '#a9c3be'; MINT_INNER = '#d6e6e2'
CREAM_TOP = '#f7f1e2'; CREAM_SIDE = '#cdbf9f'
TEAL = '#2a8c80'; ORANGE = '#e0874a'

# ---------------------------------------------------------------- sprites
def station():
    reset()
    H = 0.30
    cyl(0.60, H, 0, mat(MINT_SIDE), INK)
    cyl(0.56, 0.03, 0.012, mat(MINT_TOP), None, bevel=0.012)
    cyl(0.40, 0.03, 0.022, mat(MINT_INNER), INK, bevel=0.01)
    torus(0.48, 0.018, 0.02, mat('#c3d6d2'))
    # four little rivets
    for a in range(4):
        ang = math.radians(45 + 90 * a)
        cyl(0.03, 0.03, 0.03, mat('#8fb0aa'), None, verts=16, bevel=0.008, x=0.5 * math.cos(ang), y=0.5 * math.sin(ang))
    ground(-H)
    render('station', 1.8, 1.8)

def switch():
    reset()
    H = 0.26
    cyl(0.48, H, 0, mat(CREAM_SIDE), INK_WARM)
    cyl(0.45, 0.03, 0.012, mat(CREAM_TOP), None, bevel=0.012)
    torus(0.40, 0.016, 0.02, mat('#e3d8bd'))
    ground(-H)
    render('switch', 1.5, 1.5, ink=INK_WARM)

def mailbox():
    reset()
    H = 0.30
    cyl(0.64, H, 0, mat(MINT_SIDE), INK)
    cyl(0.60, 0.03, 0.012, mat(MINT_TOP), None, bevel=0.012)
    box(0.70, 0.46, 0.08, (0, 0, 0.05), mat(TEAL, 0.45), INK, bevel=0.02, thick=0.015)
    for s in (-1, 1):
        box(0.43, 0.035, 0.02, (s * 0.165, 0.10, 0.095), mat('#eef5f3'), None, bevel=0.008, rot=(0, 0, s * math.radians(-33)))
    ground(-H)
    render('mailbox', 1.8, 1.8)

def recycler():
    reset()
    H = 0.30
    cyl(0.64, H, 0, mat('#c9c0ad'), INK_WARM)
    cyl(0.60, 0.03, 0.012, mat('#f6f1e6'), None, bevel=0.012)
    for s in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.065, depth=0.62, location=(0, 0, 0.08),
                                            rotation=(0, math.radians(90), s * math.radians(38)))
        finish(bpy.context.object, mat(ORANGE, 0.4), '#9a5a2e', bevel=0.05, thick=0.012)
    cyl(0.07, 0.08, 0.16, mat(INK), None, verts=24, bevel=0.02)
    ground(-H)
    render('recycler', 1.8, 1.8, ink=INK_WARM)

def factory():
    reset()
    H = 0.75
    # main hall
    box(2.0, 1.6, H, (0, 0, -H / 2), mat('#e3ebe9'), INK, bevel=0.06)
    box(1.88, 1.48, 0.04, (0, 0, 0.01), mat('#f2f6f5'), None, bevel=0.015)
    # teal sign band along the front
    box(2.02, 0.05, 0.12, (0, -0.80, -0.12), mat(TEAL, 0.45), None, bevel=0.02)
    # press / hopper on the roof (left)
    box(0.95, 0.72, 0.40, (-0.42, 0.20, 0.20), mat('#f4f7f6'), INK, bevel=0.05)
    box(0.80, 0.05, 0.22, (-0.42, -0.165, 0.20), mat('#d6e2df'), None, bevel=0.02)
    for i in range(3):
        box(0.62, 0.02, 0.025, (-0.42, -0.195, 0.13 + i * 0.07), mat('#7c9c96'), None, bevel=0.006)
    box(0.60, 0.46, 0.10, (-0.42, 0.20, 0.43), mat('#cfdedb'), INK, bevel=0.03)
    # output chute (right) – the waiting tile sits here
    box(0.64, 0.64, 0.05, (0.60, -0.02, 0.02), mat('#2f4f4b', 0.8), INK, bevel=0.025)
    box(0.74, 0.74, 0.04, (0.60, -0.02, 0.005), mat('#9fb8b3'), None, bevel=0.02)
    # front windows and door
    for x in (-0.74, -0.44, -0.14):
        box(0.20, 0.04, 0.20, (x, -0.80, -0.42), mat('#6b8f89', 0.3), None, bevel=0.015)
    box(0.42, 0.04, 0.40, (0.55, -0.80, -0.55), mat('#2f4f4b', 0.8), None, bevel=0.03)
    # small stack with a cap at the back
    cyl(0.10, 0.45, 0.48, mat('#d6e2df'), INK, verts=32, bevel=0.02, x=0.30, y=0.58)
    cyl(0.14, 0.06, 0.52, mat(TEAL, 0.45), INK, verts=32, bevel=0.02, x=0.30, y=0.58)
    ground(-H)
    render('factory', 3.3, 3.3)

def tile(name, top, edge):
    reset()
    H = 0.16
    box(0.52, 0.52, H, (0, 0, -H / 2), mat(top), edge, bevel=0.09, thick=0.03)
    ground(-H)
    render(name, 0.9, 0.9, ink=edge, ink_px=4)

for f in (station, switch, mailbox, recycler, factory):
    f()
tile('tile', '#eef6f3', '#2f6f68')
tile('tile_scrap', '#f3d6d0', '#b65050')
print('ALL DONE')
