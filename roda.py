# ESTÚDIO 3D — DESENHO NA NUVEM de um projeto feito na página (Hidra/frontend/estudio_3d.html), 11/11.
# Lê projeto.json (elenco, marcas, falas) e pedido.json {de, ate, fps, amostras, largura, altura}; calcula a pose de cada
# boneco em cada quadro com A MESMA CONTA da página (marcas interpoladas, passos ao andar, ossos girados pai→filho, boca nas
# falas) e desenha no Blender. Devolve saida/parte.mp4 (sem som; o som entra depois, em estudio3d_nuvem.js).
import bpy, os, sys, json, math, time, subprocess
sys.path.insert(0, os.path.abspath('.'))
bpy.ops.wm.read_factory_settings(use_empty=True)
import elenco3d as E, palco3d as PL
from mathutils import Matrix

S = bpy.context.scene
PROJ = json.load(open('projeto.json', encoding='utf8')); PED = json.load(open('pedido.json', encoding='utf8'))
CAT = json.load(open('bonecos.json', encoding='utf8')); MOVS = {m['id']: m for m in CAT['movimentos']}
FPS = int(PED.get('fps', 12)); S.render.fps = FPS
# 11/11: além do teatro, o cenário da fazenda da Turminha do Brejo (turminha3d.py), com o chão na altura 0
CHAO = PL.ALT
if PROJ.get('cenario', 'teatro') == 'fazenda':
    import turminha3d as T3; T3.fazenda(S, PROJ.get('hora', 'dia')); CHAO = 0.0
else:
    PL.montar(E); PL.luzes(S); PL.camera(S)

FAZ = {'rato': E.rato, 'latinha': E.latinha, 'saco_azul': lambda: E.saco('Saco de lixo I', '#1f4fa8'), 'saco_preto': lambda: E.saco('Saco de lixo II', '#24242a'),
       'mulher': lambda: E.pessoa('Mulher', 2.35, '#e7b08c', '#7a3b1a', 'longo', '#d9579a', '#000000', saia='#7c4fb0', sapato='#8a2040', sujo=True),
       'marido': lambda: E.pessoa('Marido', 2.55, '#c98e66', '#2b1a10', 'curto', '#3f8f5a', '#3b4766', sujo=True),
       'garoto': lambda: E.pessoa('Garoto', 1.75, '#9a6a4a', '#1a120c', 'bone', '#f2c230', '#3a64b8', sapato='#ffffff'),
       'mae': lambda: E.pessoa('Mãe', 2.35, '#f0c4a0', '#3a2414', 'coque', '#3aa6a0', '#000000', saia='#e0884a', sapato='#5a3a20'),
       'chuva': E.chuva, 'rio': E.rio}
try:   # a Turminha do Brejo em 3D (teste de comparação, 11/11)
    import turminha3d as T3
    FAZ.update({'timbu': T3.timbu, 'poe_mesa': T3.poe_mesa, 'tagarela': T3.tagarela, 'caio': T3.caio, 'barbicha': T3.barbicha, 'dona_filo': T3.dona_filo})
except ImportError: pass
BON = {}
for it in PROJ['elenco']:
    b = FAZ[it['boneco']](); BON[it['uid']] = b
    if getattr(b, 'boca', None): b.boca['z0'] = b.boca.scale.z

def nivel(b, osso):
    k, o = 0, b.arm.data.bones[osso]
    while o.parent: k += 1; o = o.parent
    return k
def estado(uid, t):
    ms = sorted(PROJ['marcas'].get(uid, []), key=lambda m: m['t'])
    if not ms: return None
    if t <= ms[0]['t']: return dict(ms[0], andando=False)
    for a, b in zip(ms, ms[1:]):
        if a['t'] <= t <= b['t']:
            u = (t - a['t']) / max(1e-6, b['t'] - a['t']); mix = lambda p, q: p + (q - p) * u
            mov = {k: mix(a['mov'].get(k, 0), b['mov'].get(k, 0)) for k in set(a['mov']) | set(b['mov'])}
            dist = math.hypot(b['x'] - a['x'], b['y'] - a['y'])
            return {'x': mix(a['x'], b['x']), 'y': mix(a['y'], b['y']), 'z': mix(a.get('z', 0), b.get('z', 0)), 'giro': mix(a['giro'], b['giro']),
                    'mov': mov, 'andando': dist > 0.3 and not b.get('semPassos'), 'fase': t - a['t']}
    return dict(ms[-1], andando=False)
def aplicar(uid, t):
    b, e = BON[uid], estado(uid, t)
    if not e: return
    mov, z = dict(e['mov']), e.get('z', 0)
    if e['andando']:
        s = math.sin(e['fase'] * math.pi * 2 / 0.56); mov['perna_e_passo'] = 22 * s; mov['perna_d_passo'] = -22 * s; z += 0.05 * abs(s)
    b.arm.location = (e['x'], e['y'], CHAO + z); b.arm.rotation_euler = (0, 0, math.radians(e['giro']))
    for pb in b.arm.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    ms = sorted((m for k, m in MOVS.items() if mov.get(k) and m['osso'] in b.arm.pose.bones), key=lambda m: nivel(b, m['osso']))
    for m in ms: b.girar(m['osso'], m['eixo'], mov[m['id']] * m['sinal'])
    bo = getattr(b, 'boca', None)
    if bo:
        f = next((f for f in PROJ.get('falas', []) if f['uid'] == uid and f['ini'] <= t <= f['fim']), None)
        bo.scale.z = bo['z0'] * ((1.2 if int((t - f['ini']) / 0.12) % 2 else 2.8) if f else 1)

# 11/11: Cycles levou 24 s por quadro (a peça inteira daria ~30 h) → o padrão passa a ser o EEVEE (desenha como videogame,
# muito mais rápido; para bonecos de desenho a diferença quase não aparece). 'motor': 'cycles' volta ao jeito antigo.
if PED.get('motor', 'eevee') == 'cycles':
    S.render.engine = 'CYCLES'; S.cycles.device = 'CPU'; S.cycles.samples = int(PED.get('amostras', 12)); S.cycles.use_denoising = True
    S.cycles.max_bounces = 4; S.render.use_persistent_data = True
else:
    S.render.engine = 'BLENDER_EEVEE_NEXT'; S.eevee.taa_render_samples = int(PED.get('amostras', 32))
    try: S.eevee.use_shadows = True
    except Exception: pass
S.render.resolution_x, S.render.resolution_y = int(PED.get('largura', 960)), int(PED.get('altura', 540))
S.render.use_freestyle = True; S.render.line_thickness_mode = 'ABSOLUTE'; S.render.line_thickness = 1.2
S.view_settings.view_transform = 'AgX'
os.makedirs('saida', exist_ok=True); Q = os.path.abspath('quadros'); os.makedirs(Q, exist_ok=True)
n0, n1 = int(round(PED['de'] * FPS)), int(round(PED['ate'] * FPS)); inicio = time.time()
for k in range(n0, n1 + 1):
    t = k / FPS
    for uid in BON: aplicar(uid, t)
    bpy.context.view_layer.update()
    S.render.filepath = os.path.join(Q, f'q{k:06d}.png'); bpy.ops.render.render(write_still=True)
    if (k - n0) % FPS == 0: print(f'quadro {k - n0 + 1}/{n1 - n0 + 1} · {(time.time() - inicio) / (k - n0 + 1):.1f} s por quadro', flush=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-start_number', str(n0), '-i', os.path.join(Q, 'q%06d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', os.path.join('saida', 'parte.mp4')], check=True)
open(os.path.join('saida', 'tempo.txt'), 'w').write(f'{n1 - n0 + 1} quadros em {time.time() - inicio:.0f} s')
print('pronto', flush=True)
