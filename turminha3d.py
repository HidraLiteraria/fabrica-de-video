# TURMINHA DO BREJO EM 3D (11/11) — teste de comparação pedido pelo Wagner ("só um desse da turminha do brejo… para comparar o que
# tínhamos antigamente, o que temos agora e o que pode ser feito lá no GitHub"). Os 6 personagens da série "Não Sou Quem Você
# Pensa!" refeitos como bonecos com esqueleto (mesmo método de elenco3d.py), fiéis aos desenhos de referência:
# Timbu (saruê branco de orelhas pretas), Põe-Mesa (louva-a-deus verde de cabeça triangular), Tagarela (papagaio verde com
# coroa azul e amarela), Caio (menino de cabelo crespo, camiseta amarela, short azul), Barbicha (cágado de óculos, casco escuro)
# e Dona Filó (vovó de coque, vestido florido azul e avental). + o cenário da fazenda.
import bpy, math
from mathutils import Vector
import elenco3d as E
from elenco3d import mat, esfera, cilindro, caixa, membro, Boneco

def timbu():
    """saruê: bicho de 4 patas; as patas da frente usam os ossos braco_e/d (assim ele 'acena' com a pata)"""
    BR, PR, ROSA = mat('timbu_pelo', '#f4f2f0', 0.85), mat('timbu_preto', '#1e1e22', 0.6), mat('timbu_rosa', '#f2a5b8', 0.5)
    B = Boneco('Timbu', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0.1, 0.45), (0, -0.3, 0.6), 'raiz'), ('cabeca', (0, -0.35, 0.6), (0, -0.55, 1.0), 'corpo'),
                         ('braco_e', (0.18, -0.35, 0.45), (0.2, -0.38, 0.05), 'corpo'), ('braco_d', (-0.18, -0.35, 0.45), (-0.2, -0.38, 0.05), 'corpo'),
                         ('perna_e', (0.2, 0.35, 0.45), (0.22, 0.35, 0.05), 'raiz'), ('perna_d', (-0.2, 0.35, 0.45), (-0.22, 0.35, 0.05), 'raiz'),
                         ('cauda1', (0, 0.6, 0.5), (0, 1.0, 0.75), 'raiz'), ('cauda2', (0, 1.0, 0.75), (0, 1.1, 1.05), 'cauda1')])
    B.prende(esfera('corpo', (0, 0.1, 0.55), (0.33, 0.55, 0.32), BR), 'corpo')
    B.prende(esfera('cabeca', (0, -0.5, 0.82), (0.3, 0.32, 0.28), BR), 'cabeca')
    B.prende(esfera('focinho', (0, -0.78, 0.76), (0.12, 0.16, 0.11), BR), 'cabeca')
    B.prende(esfera('nariz', (0, -0.93, 0.78), (0.05, 0.04, 0.045), ROSA), 'cabeca')
    for lado, s in ((1, 'e'), (-1, 'd')):
        B.prende(esfera('orelha', (0.22 * lado, -0.42, 1.08), (0.14, 0.05, 0.15), PR), 'cabeca')
        B.prende(esfera('mancha', (0.13 * lado, -0.72, 0.9), (0.09, 0.04, 0.07), mat('timbu_mancha', '#3a3a40', 0.6), 0), 'cabeca')
        B.prende(membro('pata', (0.18 * lado, -0.35, 0.45), (0.2 * lado, -0.38, 0.08), 0.07, BR), 'braco_' + s)
        B.prende(esfera('pe', (0.2 * lado, -0.42, 0.04), (0.08, 0.1, 0.05), ROSA), 'braco_' + s)
        B.prende(membro('pata_tras', (0.2 * lado, 0.35, 0.45), (0.22 * lado, 0.35, 0.08), 0.08, BR), 'perna_' + s)
        B.prende(esfera('pe_tras', (0.22 * lado, 0.3, 0.04), (0.08, 0.11, 0.05), ROSA), 'perna_' + s)
    B.rosto('cabeca', (0, -0.74, 0.92), 0.12, 0.07, boca=False)
    b = esfera('boca', (0, -0.86, 0.68), (0.05, 0.02, 0.018), mat('boca', '#5a1f2b', 0.4)); B.prende(b, 'cabeca'); B.boca = b
    cd = bpy.data.curves.new('rabo_timbu', 'CURVE'); cd.dimensions = '3D'; cd.bevel_depth = 0.035; cd.bevel_resolution = 4
    sp = cd.splines.new('BEZIER'); sp.bezier_points.add(2)
    for p, c in zip(sp.bezier_points, [(0, 0.6, 0.5), (0, 1.0, 0.7), (0, 1.05, 1.05)]): p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    rb = bpy.data.objects.new('rabo', cd); bpy.context.collection.objects.link(rb); rb.data.materials.append(ROSA); B.prende(rb, 'cauda1')
    return B

def poe_mesa():
    """louva-a-deus: corpo fino verde, cabeça triangular com olhos grandes"""
    VD, VC = mat('louva_verde', '#7cc35a', 0.5), mat('louva_claro', '#a6dc84', 0.5)
    B = Boneco('Põe-Mesa', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 0.9), (0, 0, 1.55), 'raiz'), ('cabeca', (0, 0, 1.55), (0, 0, 2.3), 'corpo'),
                            ('braco_e', (0.2, 0, 1.45), (0.35, -0.05, 0.95), 'corpo'), ('braco_d', (-0.2, 0, 1.45), (-0.35, -0.05, 0.95), 'corpo'),
                            ('perna_e', (0.1, 0, 0.9), (0.12, 0, 0.05), 'raiz'), ('perna_d', (-0.1, 0, 0.9), (-0.12, 0, 0.05), 'raiz')])
    B.prende(esfera('tronco', (0, 0, 1.2), (0.2, 0.15, 0.38), VD), 'corpo')
    B.prende(membro('pescoco', (0, 0, 1.5), (0, 0, 1.68), 0.06, VD), 'cabeca')
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0.0, depth=0.75, location=(0, 0, 1.95), rotation=(math.pi, 0, 0), vertices=4)
    c = bpy.context.object; c.name = 'cabeca_triangular'; c.scale = (1.15, 0.55, 1); c.rotation_euler = (math.pi, 0, math.pi / 4); c.data.materials.append(VD); E._liso(c, 2); B.prende(c, 'cabeca')
    B.prende(esfera('topo', (0, 0, 2.18), (0.22, 0.15, 0.16), VD), 'cabeca')
    B.rosto('cabeca', (0, -0.15, 2.05), 0.13, 0.085, boca=False)
    b = esfera('boca', (0, -0.15, 1.82), (0.05, 0.02, 0.018), mat('boca', '#3b5a22', 0.4)); B.prende(b, 'cabeca'); B.boca = b
    E._bracos_pernas(B, (0.19, 0, 1.45), (0.34, -0.05, 0.98), (0.1, 0, 0.9), (0.12, 0, 0.0), 0.045, 0.055, VD, VC, VD, VC)
    return B

def tagarela():
    """papagaio verde com a coroa azul e amarela; as asas usam os ossos braco_e/d"""
    VD, AZ, AM, BI = mat('papagaio_verde', '#43a83c', 0.5), mat('papagaio_azul', '#2f5fd0', 0.4), mat('papagaio_amarelo', '#f2d33a', 0.4), mat('bico', '#4a4d55', 0.3)
    B = Boneco('Tagarela', [('raiz', (0, 0, 0), (0, 0, 0.2), None), ('corpo', (0, 0, 0.25), (0, 0, 0.8), 'raiz'), ('cabeca', (0, 0, 0.8), (0, 0, 1.3), 'corpo'),
                            ('braco_e', (0.28, 0.02, 0.75), (0.32, 0.08, 0.3), 'corpo'), ('braco_d', (-0.28, 0.02, 0.75), (-0.32, 0.08, 0.3), 'corpo'),
                            ('perna_e', (0.1, 0, 0.25), (0.1, 0, 0.0), 'raiz'), ('perna_d', (-0.1, 0, 0.25), (-0.1, 0, 0.0), 'raiz')])
    B.prende(esfera('corpo', (0, 0.05, 0.6), (0.3, 0.28, 0.42), VD, rot=(0.25, 0, 0)), 'corpo')
    B.prende(esfera('barriga', (0, -0.15, 0.55), (0.2, 0.12, 0.3), mat('papagaio_claro', '#7fd06a', 0.5)), 'corpo')
    B.prende(esfera('cabeca', (0, -0.05, 1.05), (0.26, 0.25, 0.25), VD), 'cabeca')
    B.prende(esfera('coroa_azul', (0, -0.1, 1.2), (0.2, 0.16, 0.1), AZ), 'cabeca')
    B.prende(esfera('coroa_amarela', (0, -0.18, 1.14), (0.16, 0.1, 0.07), AM), 'cabeca')
    bpy.ops.mesh.primitive_cone_add(radius1=0.09, radius2=0.01, depth=0.22, location=(0, -0.33, 1.0), rotation=(math.radians(120), 0, 0), vertices=24)
    c = bpy.context.object; c.name = 'bico'; c.data.materials.append(BI); E._liso(c, 1); B.prende(c, 'cabeca')
    B.rosto('cabeca', (0, -0.22, 1.08), 0.12, 0.06, boca=False)
    b = esfera('boca', (0, -0.3, 0.93), (0.04, 0.02, 0.015), BI); B.prende(b, 'cabeca'); B.boca = b
    for lado, s in ((1, 'e'), (-1, 'd')):
        B.prende(esfera('asa', (0.3 * lado, 0.08, 0.55), (0.08, 0.2, 0.32), VD, rot=(0.2, -0.15 * lado, 0)), 'braco_' + s)
        B.prende(esfera('ponta_asa', (0.31 * lado, 0.18, 0.28), (0.06, 0.12, 0.12), AZ), 'braco_' + s)
        B.prende(esfera('pe', (0.1 * lado, -0.06, 0.04), (0.07, 0.1, 0.04), BI), 'perna_' + s)
    B.prende(esfera('cauda', (0, 0.3, 0.25), (0.12, 0.08, 0.3), VD, rot=(-0.6, 0, 0)), 'raiz')
    return B

def barbicha():
    """cágado de pé, casco escuro, pescoço comprido e óculos redondos"""
    VD, CASCO, BAR = mat('cagado_verde', '#79b26a', 0.6), mat('casco', '#2c2c2e', 0.5), mat('cagado_barriga', '#c9d79a', 0.6)
    B = Boneco('Barbicha', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 0.4), (0, 0, 1.2), 'raiz'), ('cabeca', (0, 0, 1.2), (0, 0, 1.9), 'corpo'),
                            ('braco_e', (0.42, -0.05, 0.95), (0.58, -0.1, 0.55), 'corpo'), ('braco_d', (-0.42, -0.05, 0.95), (-0.58, -0.1, 0.55), 'corpo'),
                            ('perna_e', (0.22, 0, 0.4), (0.24, 0, 0.0), 'raiz'), ('perna_d', (-0.22, 0, 0.4), (-0.24, 0, 0.0), 'raiz')])
    B.prende(esfera('casco', (0, 0.05, 0.8), (0.5, 0.4, 0.55), CASCO), 'corpo')
    B.prende(esfera('barriga', (0, -0.28, 0.78), (0.36, 0.12, 0.42), BAR), 'corpo')
    B.prende(membro('pescoco', (0, -0.05, 1.15), (0, -0.08, 1.6), 0.12, VD), 'cabeca')
    for k in range(3): B.prende(esfera('listra', (0, -0.18, 1.32 + k * 0.1), (0.1, 0.03, 0.02), mat('listra', '#d9e6c0', 0.6), 0), 'cabeca')
    B.prende(esfera('cabeca', (0, -0.1, 1.75), (0.22, 0.22, 0.2), VD), 'cabeca')
    B.rosto('cabeca', (0, -0.27, 1.78), 0.09, 0.06, boca=False)
    for lado in (1, -1):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.012, location=(0.09 * lado, -0.32, 1.78), rotation=(math.pi / 2, 0, 0))
        o = bpy.context.object; o.name = 'oculos'; o.data.materials.append(mat('oculos', '#3a3a3a', 0.3)); B.prende(o, 'cabeca')
    b = esfera('boca', (0, -0.3, 1.65), (0.07, 0.02, 0.02), mat('boca', '#3b2a1a', 0.4)); B.prende(b, 'cabeca'); B.boca = b
    E._bracos_pernas(B, (0.42, -0.05, 0.95), (0.56, -0.1, 0.6), (0.22, 0, 0.4), (0.24, 0, 0.0), 0.08, 0.1, VD, VD, VD, VD)
    return B

def caio():
    B = E.pessoa('Caio', 1.75, '#7a4a2e', '#1a120c', 'curto', '#f2c230', '#2f5fc4', sapato='#ffffff')
    for (x, y, z, r) in ((0, 0.02, 2.14, 0.3), (0.2, 0.0, 2.05, 0.2), (-0.2, 0.0, 2.05, 0.2), (0.12, 0.12, 2.2, 0.2), (-0.12, 0.12, 2.2, 0.2)):   # cabelo crespo
        k = 1.75 / 2.4; B.prende(esfera('crespo', (x * k, y * k, z * k), (r * k,) * 3, mat('cabelo_Caio', '#1a120c', 0.8)), 'cabeca')
    return B

def dona_filo():
    B = E.pessoa('Dona Filó', 2.1, '#e8b48f', '#bdbdbd', 'coque', '#3cc4c8', '#000000', saia='#3cc4c8', sapato='#a0703a')
    k = 2.1 / 2.4; BR = mat('avental', '#ffffff', 0.7)
    B.prende(caixa('avental', (0, -0.3 * k, 0.85 * k), (0.25 * k, 0.03 * k, 0.32 * k), BR), 'corpo')
    for (x, z, c) in ((0.15, 1.35, '#f2a33a'), (-0.18, 1.2, '#e8546a'), (0.05, 1.05, '#f2d33a'), (-0.1, 0.55, '#e8546a'), (0.3, 0.7, '#f2a33a'), (-0.3, 0.8, '#f2d33a')):   # flores do vestido
        B.prende(esfera('flor', (x * k, -0.3 * k, z * k), (0.05 * k, 0.015 * k, 0.05 * k), mat('flor' + c, c, 0.6), 0), 'corpo')
    return B

def turminha():
    return {'timbu': timbu(), 'poe_mesa': poe_mesa(), 'tagarela': tagarela(), 'caio': caio(), 'barbicha': barbicha(), 'dona_filo': dona_filo()}

def fazenda(S, hora='dia', mangueira=False):
    """o cenário: pasto verde, céu azul com sol e nuvens, celeiro vermelho, árvores, cerca e o açude ao fundo
    (11/11: no 1º teste o céu saiu cinza e faltavam o celeiro e o sol dos desenhos antigos). mangueira=True: o pé de manga
    grande à direita, com o galho onde o Tagarela pousa (x≈3.6, altura ≈2.4)."""
    S.view_settings.view_transform = 'Standard'          # cores vivas de desenho (o AgX acinzentava o céu)
    CEU = {'dia': (0.30, 0.62, 1.0, 1), 'tarde': (1.0, 0.55, 0.28, 1), 'noite': (0.02, 0.04, 0.12, 1)}[hora]
    W = bpy.data.worlds.new('ceu'); S.world = W; W.use_nodes = True; W.node_tree.nodes['Background'].inputs[0].default_value = CEU
    W.node_tree.nodes['Background'].inputs[1].default_value = 1.0 if hora != 'noite' else 0.3
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 10, 0)); g = bpy.context.object; g.name = 'pasto'; g.data.materials.append(mat('pasto', '#6dbb4a', 0.9))
    agua = cilindro('acude', (-6, 14, 0.01), 4.5, 0.02, mat('acude', '#3f8fd6', 0.1)); agua.scale = (1.6, 1, 1)
    TR, FO = mat('tronco', '#7a4b26', 0.8), mat('folhas', '#3e9a3a', 0.8)
    for (x, y, s) in ((-9, 9, 1.3), (7.5, 8, 1.6), (11, 14, 1.2), (-3, 18, 1.4), (3, 20, 1.1)):
        cilindro('tronco', (x, y, 1.2 * s), 0.25 * s, 2.4 * s, TR)
        for dx, dz, r in ((0, 3.0, 1.4), (-0.8, 2.6, 1.0), (0.8, 2.6, 1.0)): esfera('copa', (x + dx * s, y, dz * s), (r * s, r * s, r * s * 0.9), FO)
    MAD = mat('cerca', '#a87b4f', 0.8)
    for k in range(-10, 11):
        cilindro('mourao', (k * 1.4, 5.5, 0.55), 0.07, 1.1, MAD)
    for z in (0.45, 0.85): caixa('ripa', (0, 5.5, z), (14.5, 0.04, 0.05), MAD)
    # o celeiro vermelho (como nos desenhos), com telhado e portas em X brancas
    VERM, BRANCO = mat('celeiro', '#c8302c', 0.7), mat('branco_celeiro', '#f4f4f4', 0.6)
    caixa('celeiro', (5.5, 11, 1.8), (2.2, 1.8, 1.8), VERM)
    bpy.ops.mesh.primitive_cone_add(radius1=3.4, depth=1.6, location=(5.5, 11, 4.4), vertices=4, rotation=(0, 0, math.pi / 4))
    t = bpy.context.object; t.name = 'telhado'; t.scale = (0.92, 0.75, 1); t.data.materials.append(mat('telhado', '#7a1f1c', 0.7))
    caixa('porta', (5.5, 9.18, 1.3), (0.9, 0.03, 1.3), BRANCO)
    for a in (0.95, -0.95): caixa('x_porta', (5.5, 9.14, 1.3), (1.05, 0.025, 0.07), VERM, rot=(0, a, 0))
    if hora != 'noite':   # o sol e as nuvens
        esfera('sol', (-9, 30, 12), (1.6, 1.6, 1.6), mat('sol', '#ffd84a', 0.5, 6.0), 0)
        NUV = mat('nuvem_ceu', '#ffffff', 0.9, 0.6)
        for (x, z) in ((-6, 9.5), (2, 10.5), (9, 9)):
            for dx, r in ((0, 1.2), (-1.1, 0.9), (1.1, 0.9)): esfera('nuvem', (x + dx, 26, z), (r, r * 0.6, r * 0.7), NUV, 0)
    else:
        esfera('lua', (-8, 30, 11), (1.2, 1.2, 1.2), mat('lua', '#f2f0d8', 0.5, 4.0), 0)
    if mangueira:   # o pé de manga grande à direita, com o galho do Tagarela
        cilindro('tronco_manga', (4.6, 1.5, 1.6), 0.35, 3.2, TR)
        membro('galho', (4.4, 1.5, 2.3), (3.4, 1.0, 2.35), 0.12, TR)
        for dx, dz, r in ((0, 4.2, 1.9), (-1.3, 3.7, 1.3), (1.2, 3.7, 1.3), (-0.6, 4.9, 1.2)): esfera('copa_manga', (4.6 + dx, 1.8, dz), (r, r, r * 0.85), FO)
        for dx, dz in ((-0.8, 3.0), (0.6, 3.1), (1.4, 3.6)): esfera('manga', (4.6 + dx, 0.9, dz), (0.13, 0.11, 0.17), mat('manga', '#f2a23a', 0.5), 0)
    sol = bpy.data.lights.new('sol', 'SUN'); sol.energy = 3.5 if hora != 'noite' else 0.4; sol.angle = math.radians(8)
    o = bpy.data.objects.new('sol', sol); S.collection.objects.link(o); o.rotation_euler = (math.radians(50), 0, math.radians(30))
    d = bpy.data.lights.new('rebatedor', 'AREA'); d.energy = 600; d.size = 8
    o = bpy.data.objects.new('rebatedor', d); S.collection.objects.link(o); o.location = (0, -8, 4); o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); S.collection.objects.link(c); S.camera = c
    c.location = (0, -8.5, 1.9); c.rotation_euler = (Vector((0, 0, 1.0)) - c.location).to_track_quat('-Z', 'Y').to_euler(); c.data.lens = 35
