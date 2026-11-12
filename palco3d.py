# O PALCO DO TEATRO 3D (11/11) — o mesmo para a peça, para a exportação ao navegador (Estúdio 3D) e para o desenho na nuvem:
# chão de madeira, a "rua" com o bueiro, o fundo com prédios pintados, a moldura dourada, as cortinas e a plateia de costas.
import bpy, math
from mathutils import Vector
ALT = 0.9                                                    # altura do palco
ABERTA, FECHADA = 9.4, 3.2                                   # onde fica cada cortina (x)

def montar(E):
    P = {'pecas': [], 'cabecas': []}; add = lambda o: (P['pecas'].append(o), o)[1]
    add(E.caixa('palco', (0, 1.5, ALT / 2), (6.5, 3.5, ALT / 2), E.mat('madeira', '#7a4a26', 0.6)))
    add(E.caixa('rua_cenario', (0, 0.9, ALT + 0.01), (5.0, 1.9, 0.01), E.mat('asfalto', '#5d5f66', 0.9)))
    add(E.caixa('calcada', (0, 2.9, ALT + 0.08), (5.0, 0.3, 0.08), E.mat('calcada', '#a9a39a', 0.9)))
    add(E.caixa('fundo', (0, 5, 3.5), (7, 0.1, 3.5), E.mat('fundo_ceu', '#2b3d6b', 0.9)))
    for k, (x, h) in enumerate(((-4.2, 2.6), (-3.0, 3.6), (-1.6, 2.2), (2.0, 3.0), (3.4, 2.4), (4.6, 3.8))):
        add(E.caixa('predio', (x, 4.85, ALT + h / 2), (0.55, 0.05, h / 2), E.mat('predio%d' % (k % 3), ('#38507f', '#2f4470', '#41598a')[k % 3], 0.9)))
    add(E.cilindro('bueiro', (1.2, 0.9, ALT + 0.03), 0.55, 0.04, E.mat('ferro', '#2a2a2e', 0.4)))
    for k in range(-4, 5): add(E.caixa('grade', (1.2 + k * 0.11, 0.9, ALT + 0.06), (0.025, 0.42 * math.cos(math.asin(min(1, abs(k) * 0.11 / 0.55))), 0.015), E.mat('ferro_claro', '#4a4a52', 0.3)))
    OURO, VERM = E.mat('ouro', '#d4a017', 0.3), E.mat('cortina', '#a3121f', 0.7)
    for n, loc, esc in (('moldura_topo', (0, -1.9, 6.2), (6.5, 0.25, 0.45)), ('moldura_e', (6.2, -1.9, 3), (0.35, 0.25, 3.2)), ('moldura_d', (-6.2, -1.9, 3), (0.35, 0.25, 3.2))):
        add(E.caixa(n, loc, esc, OURO))
    for nome, x, larg, alt, z in (('cortina_e', ABERTA, 6.5, 5.9, 3.85), ('cortina_d', -ABERTA, 6.5, 5.9, 3.85), ('bambinela', 0, 13.0, 1.3, 5.6)):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=6, size=1, location=(x, -1.6 if nome != 'bambinela' else -1.7, z), rotation=(math.pi / 2, 0, 0))
        o = bpy.context.object; o.name = nome; o.scale = (larg, alt, 1); o.data.materials.append(VERM)
        for v in o.data.vertices: v.co.z += 0.05 * math.sin(v.co.x * 90)
        E._liso(o, 1); P[nome] = add(o)
    GENTE = [E.mat('plateia%d' % i, c, 0.9) for i, c in enumerate(('#1c1c26', '#262033', '#1f2a2a', '#2e2222'))]
    for fila, (y, z, n) in enumerate(((-4.6, 1.15, 9), (-6.0, 1.45, 10))):
        for k in range(n):
            x = (k - (n - 1) / 2) * 1.35 + (0.3 if fila else 0); m = GENTE[(k + fila) % 4]
            add(E.esfera('ombros', (x, y, z - 0.45), (0.42, 0.25, 0.3), m, 0)); P['cabecas'].append(add(E.esfera('cabeca_pub', (x, y, z), (0.21, 0.23, 0.26), m, 0)))
    return P

def luzes(S):
    def luz(nome, tipo, loc, energia, alvo=None, cor=(1, 1, 1), tam=1.0):
        d = bpy.data.lights.new(nome, tipo); d.energy = energia; d.color = cor
        if tipo == 'AREA': d.size = tam
        if tipo == 'SPOT': d.spot_size = math.radians(tam); d.spot_blend = 0.4
        o = bpy.data.objects.new(nome, d); S.collection.objects.link(o); o.location = loc
        if alvo: o.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        return o
    W = bpy.data.worlds.new('mundo'); S.world = W; W.use_nodes = True; W.node_tree.nodes['Background'].inputs[0].default_value = (0.01, 0.01, 0.015, 1)
    # 11/11: no 1º teste o palco ficou escuro e o rosto da Mulher sumiu → mais luz e uma luz de FRENTE (da plateia) nos rostos
    return {'canhao': luz('canhao', 'SPOT', (0, -3.5, 7.5), 5000, (0, 1.0, ALT + 0.6), (1, 0.92, 0.78), 70),
            'le': luz('lateral_e', 'SPOT', (4.5, -2.5, 6), 2500, (0, 1.2, ALT), (1, 0.85, 0.7), 60),
            'ld': luz('lateral_d', 'SPOT', (-4.5, -2.5, 6), 2500, (0, 1.2, ALT), (0.85, 0.9, 1), 60),
            'frente': luz('frente', 'AREA', (0, -6.5, 3.2), 900, (0, 1.0, ALT + 1.0), (1, 0.97, 0.92), 7),
            'fundo': luz('contraluz', 'AREA', (0, 4.6, 6), 500, (0, 0, 0), (0.6, 0.7, 1), 8)}

def camera(S):
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); S.collection.objects.link(c); S.camera = c
    # 11/11: um pouco mais perto (lente 36) — no 1º teste os bonecos ficaram pequenos
    c.location = (0, -9.5, 2.4); c.rotation_euler = (Vector((0, 1.0, 1.7)) - c.location).to_track_quat('-Z', 'Y').to_euler(); c.data.lens = 36
    return c
