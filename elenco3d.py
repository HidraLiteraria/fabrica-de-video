# "Vida no Bueiro" — BIBLIOTECA DE BONECOS 3D (11/11). Cada personagem é montado UMA vez, com formas simples, e cada peça fica
# presa a um OSSO do esqueleto: as poses saem só girando os ossos (girar / pose), nunca gerando imagem nova.
# Wagner 11/11: visual do Rato e do palco APROVADO; elenco = o do LIVRO (Daniel Fernandes e Rhalf Márcio): Rato, Latinha, Saco de
# lixo I e II, Mulher, Marido, Garoto, Mãe, Chuva, Rio; Deus = só voz + luz dourada (sem figura).
# Personagem olha para -Y (para a plateia); +X = o lado ESQUERDO dele. Unidade ≈ 1 m de palco "de brinquedo".
import bpy, math
from mathutils import Vector, Matrix

def mat(nome, cor, rug=0.55, brilho=0.0, transm=0.0):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = bpy.data.materials.new(nome); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    h = cor.lstrip('#'); rgb = [(int(h[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4)]
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rug
    if brilho: b.inputs['Emission Color'].default_value = (*rgb, 1); b.inputs['Emission Strength'].default_value = brilho
    if transm: b.inputs['Transmission Weight'].default_value = transm
    return m

def _liso(o, sub):
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
    if sub: md = o.modifiers.new('sub', 'SUBSURF'); md.levels = md.render_levels = sub

def esfera(nome, loc, esc, m, sub=1, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=loc, rotation=rot, segments=32, ring_count=16)
    o = bpy.context.object; o.name = nome; o.scale = esc; o.data.materials.append(m); _liso(o, sub); return o

def cilindro(nome, loc, r, h, m, rot=(0, 0, 0), v=32, sub=0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object; o.name = nome; o.data.materials.append(m); _liso(o, sub); return o

def caixa(nome, loc, esc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = nome; o.scale = esc; o.data.materials.append(m); return o

def membro(nome, a, b, raio, m, ponta=0.5):
    """um 'charuto' liso indo do ponto a ao ponto b (braço, perna, rabo…)"""
    a, b = Vector(a), Vector(b); d = b - a
    o = esfera(nome, (a + b) / 2, (raio, raio, d.length / 2 + raio * ponta), m)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y'); return o

PRETO, BRANCO = mat('preto', '#15151c', 0.15), mat('branco', '#ffffff', 0.2)
BRILHO = mat('brilho_olho', '#ffffff', 0.1, 2.0)

class Boneco:
    def __init__(self, nome, ossos):
        """ossos = [(nome, cabeça, ponta, pai)]"""
        bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
        self.arm = arm = bpy.context.object; arm.name = nome; ed = arm.data.edit_bones; ed.remove(ed[0])
        for n, a, b, pai in ossos:
            o = ed.new(n); o.head, o.tail = Vector(a), Vector(b)
            if pai: o.parent = ed[pai]
        bpy.ops.object.mode_set(mode='OBJECT'); self.nome = nome; self.pecas = []
    def prende(self, o, osso):
        bpy.context.view_layer.update(); mw = o.matrix_world.copy()
        o.parent = self.arm; o.parent_type = 'BONE'; o.parent_bone = osso
        bpy.context.view_layer.update(); o.matrix_world = mw; self.pecas.append(o); return o
    def rosto(self, osso, c, larg, olho=0.11, boca=True, cilios=False, sobr=None):
        """olhos grandes e brilhantes + boca sorrindo (a boca é um objeto 'boca' — abre e fecha na fala)"""
        c = Vector(c)
        for lado in (1, -1):
            self.prende(esfera('olho', c + Vector((larg * lado, 0, 0)), (olho, olho * 0.6, olho * 1.15), BRANCO), osso)
            self.prende(esfera('pupila', c + Vector((larg * lado, -olho * 0.5, -olho * 0.08)), (olho * 0.62, olho * 0.35, olho * 0.75), PRETO), osso)
            self.prende(esfera('brilho', c + Vector((larg * lado + olho * 0.2, -olho * 0.82, olho * 0.25)), (olho * 0.2, olho * 0.1, olho * 0.2), BRILHO, 0), osso)
            if sobr: self.prende(membro('sobrancelha', c + Vector((larg * lado - olho * 0.6, -olho * 0.5, olho * 1.5)), c + Vector((larg * lado + olho * 0.6, -olho * 0.5, olho * 1.45)), olho * 0.13, sobr), osso)
            if cilios: self.prende(membro('cilio', c + Vector((larg * lado + olho * 0.7 * lado, -olho * 0.4, olho * 0.9)), c + Vector((larg * lado + olho * 1.1 * lado, -olho * 0.5, olho * 1.25)), olho * 0.08, PRETO), osso)
        if boca:
            b = esfera('boca', c + Vector((0, -olho * 0.55, -olho * 2.0)), (larg * 0.75, olho * 0.3, olho * 0.28), mat('boca', '#5a1f2b', 0.4))
            self.prende(b, osso); self.boca = b
    def girar(self, osso, eixo, graus):
        """gira o osso em volta do próprio início (eixo no espaço do boneco: 'X', 'Y' ou 'Z')"""
        pb = self.arm.pose.bones[osso]; h = pb.head.copy()
        pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix
        bpy.context.view_layer.update()
    def descanso(self):
        for pb in self.arm.pose.bones: pb.matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()
    def falar(self, aberta):
        """boca aberta (fala) ou fechada — a boca só cresce na altura"""
        b = getattr(self, 'boca', None)
        if not b: return
        if 'z0' not in b: b['z0'] = b.scale.z
        b.scale.z = b['z0'] * (3.0 if aberta else 1.0)
    def mostrar(self, sim):
        for o in [self.arm] + self.pecas: o.hide_render = not sim
    def por(self, loc, giro=0):
        self.arm.location = loc; self.arm.rotation_euler = (0, 0, math.radians(giro)); bpy.context.view_layer.update(); return self

# ----------------------------------------------------------------------------------------------- os personagens
def rato():
    PELO, ROSA, BAR = mat('pelo', '#9c9a9e', 0.8), mat('rosa', '#f2a0b5', 0.5), mat('barriga', '#e9e2dc', 0.8)
    B = Boneco('Rato', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 0.35), (0, 0, 1.0), 'raiz'), ('cabeca', (0, 0, 1.0), (0, 0, 1.75), 'corpo'),
                        ('braco_e', (0.32, -0.05, 0.92), (0.5, -0.1, 0.55), 'corpo'), ('braco_d', (-0.32, -0.05, 0.92), (-0.5, -0.1, 0.55), 'corpo'),
                        ('perna_e', (0.2, 0, 0.38), (0.22, -0.05, 0.05), 'raiz'), ('perna_d', (-0.2, 0, 0.38), (-0.22, -0.05, 0.05), 'raiz'),
                        ('cauda1', (0, 0.42, 0.42), (0, 0.85, 0.3), 'raiz'), ('cauda2', (0, 0.85, 0.3), (0, 1.15, 0.65), 'cauda1')])
    B.prende(esfera('corpo', (0, 0, 0.68), (0.42, 0.38, 0.5), PELO), 'corpo')
    B.prende(esfera('barriga', (0, -0.2, 0.62), (0.3, 0.22, 0.36), BAR), 'corpo')
    B.prende(esfera('cabeca', (0, -0.02, 1.33), (0.44, 0.4, 0.38), PELO), 'cabeca')
    B.prende(esfera('focinho', (0, -0.36, 1.22), (0.2, 0.2, 0.14), BAR), 'cabeca')
    B.prende(esfera('nariz', (0, -0.55, 1.26), (0.07, 0.06, 0.06), ROSA), 'cabeca')
    B.rosto('cabeca', (0, -0.33, 1.45), 0.15, 0.11, boca=False)
    b = esfera('boca', (0, -0.52, 1.14), (0.07, 0.03, 0.025), mat('boca', '#5a1f2b', 0.4)); B.prende(b, 'cabeca'); B.boca = b
    for lado, s in ((1, 'e'), (-1, 'd')):
        for parte, esc, m, y in (('orelha', (0.24, 0.06, 0.24), PELO, 0.05), ('orelha_dentro', (0.17, 0.03, 0.17), ROSA, 0.0)):
            B.prende(esfera(parte, (0.36 * lado, y, 1.72), esc, m, rot=(0.2, 0, -0.45 * lado)), 'cabeca')
        B.prende(esfera('bochecha', (0.25 * lado, -0.3, 1.24), (0.07, 0.03, 0.05), mat('bochecha', '#f7b6c6', 0.6), 0), 'cabeca')
        for inc in (-0.12, 0.0, 0.12):
            B.prende(cilindro('bigode', (0.3 * lado, -0.47, 1.24 + inc * 0.3), 0.006, 0.38, PRETO, rot=(0, math.pi / 2, inc * lado)), 'cabeca')
        B.prende(membro('braco', (0.32 * lado, -0.05, 0.9), (0.5 * lado, -0.1, 0.6), 0.08, PELO), 'braco_' + s)
        B.prende(esfera('mao', (0.5 * lado, -0.11, 0.55), (0.08, 0.08, 0.07), ROSA), 'braco_' + s)
        B.prende(esfera('perna', (0.2 * lado, -0.02, 0.24), (0.12, 0.12, 0.18), PELO), 'perna_' + s)
        B.prende(esfera('pe', (0.22 * lado, -0.14, 0.04), (0.11, 0.2, 0.05), ROSA), 'perna_' + s)
    cd = bpy.data.curves.new('rabo', 'CURVE'); cd.dimensions = '3D'; cd.bevel_depth = 0.035; cd.bevel_resolution = 4
    sp = cd.splines.new('BEZIER'); sp.bezier_points.add(2)
    for p, c in zip(sp.bezier_points, [(0, 0.4, 0.42), (0, 0.85, 0.28), (0, 1.15, 0.68)]): p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    rb = bpy.data.objects.new('rabo', cd); bpy.context.collection.objects.link(rb); rb.data.materials.append(ROSA); B.prende(rb, 'cauda1')
    return B

def _bracos_pernas(B, ombro, mao, quadril, pe, r_braco, r_perna, m_manga, m_pele, m_calca, m_sapato):
    """braços (manga + mão) e pernas (calça + sapato) dos dois lados, presos aos ossos braco_e/d e perna_e/d"""
    for lado, s in ((1, 'e'), (-1, 'd')):
        o, m = Vector((ombro[0] * lado, ombro[1], ombro[2])), Vector((mao[0] * lado, mao[1], mao[2]))
        B.prende(membro('braco', o, m, r_braco, m_manga), 'braco_' + s)
        B.prende(esfera('mao', m + Vector((0, 0, -r_braco * 0.8)), (r_braco * 1.05,) * 3, m_pele), 'braco_' + s)
        q, p = Vector((quadril[0] * lado, quadril[1], quadril[2])), Vector((pe[0] * lado, pe[1], pe[2]))
        B.prende(membro('perna', q, p + Vector((0, 0, r_perna)), r_perna, m_calca), 'perna_' + s)
        B.prende(esfera('sapato', p + Vector((0, -r_perna * 0.6, r_perna * 0.45)), (r_perna * 1.1, r_perna * 1.8, r_perna * 0.75), m_sapato), 'perna_' + s)

def pessoa(nome, alt=2.4, pele='#e8b48f', cabelo='#3a2414', estilo='curto', camisa='#3b6fb6', calca='#2d3a55', saia=None, sapato='#2a1d15', sujo=False, olho=None):
    """gente de brinquedo: cabeça grande (desenho infantil), corpo arredondado"""
    k = alt / 2.4                                            # tudo foi desenhado para 2,4 e escala junto
    P = lambda *v: tuple(c * k for c in v)
    PELE, CAB, CAM, CAL, SAP = mat('pele_' + nome, pele, 0.6), mat('cabelo_' + nome, cabelo, 0.7), mat('camisa_' + nome, camisa, 0.75), mat('calca_' + nome, calca, 0.8), mat('sapato_' + nome, sapato, 0.4)
    B = Boneco(nome, [('raiz', (0, 0, 0), P(0, 0, 0.3), None), ('corpo', P(0, 0, 0.95), P(0, 0, 1.6), 'raiz'), ('cabeca', P(0, 0, 1.6), P(0, 0, 2.4), 'corpo'),
                      ('braco_e', P(0.36, 0, 1.5), P(0.5, -0.02, 0.95), 'corpo'), ('braco_d', P(-0.36, 0, 1.5), P(-0.5, -0.02, 0.95), 'corpo'),
                      ('perna_e', P(0.15, 0, 0.95), P(0.16, 0, 0.05), 'raiz'), ('perna_d', P(-0.15, 0, 0.95), P(-0.16, 0, 0.05), 'raiz')])
    # tronco (camisa) e, se tiver, a saia
    B.prende(esfera('tronco', P(0, 0, 1.28), P(0.36, 0.26, 0.38), CAM), 'corpo')
    B.prende(esfera('pescoco', P(0, 0, 1.62), P(0.09, 0.09, 0.08), PELE), 'cabeca')
    if saia:
        # 11/11: a 1ª saia (curta, 0,55) parecia fralda → saia até o joelho
        bpy.ops.mesh.primitive_cone_add(radius1=0.5 * k, radius2=0.3 * k, depth=0.8 * k, location=P(0, 0, 0.72), vertices=32)
        o = bpy.context.object; o.name = 'saia'; o.data.materials.append(mat('saia_' + nome, saia, 0.8)); _liso(o, 1); B.prende(o, 'corpo')
    else:
        B.prende(esfera('quadril', P(0, 0, 0.95), P(0.3, 0.22, 0.18), CAL), 'raiz')
    # cabeça grande + nariz + orelhas + rosto
    B.prende(esfera('cabeca', P(0, 0, 1.98), P(0.36, 0.33, 0.38), PELE), 'cabeca')
    B.prende(esfera('nariz', P(0, -0.33, 1.92), P(0.05, 0.05, 0.05), PELE), 'cabeca')
    for lado in (1, -1): B.prende(esfera('orelha', P(0.35 * lado, 0, 1.95), P(0.06, 0.04, 0.08), PELE), 'cabeca')
    B.rosto('cabeca', P(0, -0.27, 2.04), 0.12 * k, 0.085 * k, cilios=(estilo in ('longo', 'coque')), sobr=CAB, boca=False)
    b = esfera('boca', P(0, -0.32, 1.8), P(0.08, 0.03, 0.03), mat('boca', '#5a1f2b', 0.4)); B.prende(b, 'cabeca'); B.boca = b
    # cabelo
    B.prende(esfera('cabelo', P(0, 0.03, 2.07), P(0.38, 0.35, 0.34), CAB), 'cabeca')
    if estilo == 'longo': B.prende(esfera('cabelo_costas', P(0, 0.18, 1.82), P(0.36, 0.2, 0.42), CAB), 'cabeca')
    if estilo == 'coque': B.prende(esfera('coque', P(0, 0.22, 2.32), P(0.16, 0.16, 0.16), CAB), 'cabeca')
    if estilo == 'bone':
        B.prende(esfera('bone', P(0, 0.0, 2.2), P(0.37, 0.35, 0.2), mat('bone_' + nome, '#d63a2f', 0.6)), 'cabeca')
        B.prende(esfera('aba', P(0, -0.32, 2.18), P(0.22, 0.18, 0.03), mat('bone_' + nome, '#d63a2f', 0.6)), 'cabeca')
    _bracos_pernas(B, P(0.36, 0, 1.48), P(0.5, -0.03, 0.98), P(0.15, 0, 0.9), P(0.16, 0, 0.0), 0.085 * k, 0.11 * k, CAM, PELE, CAL if not saia else PELE, SAP)
    if sujo:                                                  # o casal da enchente: manchas de lama na roupa
        LAMA = mat('lama', '#5b4128', 0.95)
        for (x, y, z, r) in ((0.15, -0.25, 1.35, 0.07), (-0.2, -0.22, 1.15, 0.09), (0.05, -0.27, 1.05, 0.05), (-0.08, -0.25, 1.45, 0.05)):
            B.prende(esfera('lama', P(x, y, z), P(r, 0.02, r * 0.8), LAMA, 0), 'corpo')
        for lado, s in ((1, 'e'), (-1, 'd')): B.prende(esfera('lama', P(0.17 * lado, -0.1, 0.35), P(0.08, 0.02, 0.12), LAMA, 0), 'perna_' + s)
    return B

def latinha():
    LATA, PRATA = mat('lata', '#d0202a', 0.3), mat('prata', '#c9ccd1', 0.15)
    B = Boneco('Latinha', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 0.35), (0, 0, 1.35), 'raiz'),
                           ('braco_e', (0.3, 0, 0.85), (0.5, -0.05, 0.5), 'corpo'), ('braco_d', (-0.3, 0, 0.85), (-0.5, -0.05, 0.5), 'corpo'),
                           ('perna_e', (0.12, 0, 0.35), (0.13, 0, 0.0), 'raiz'), ('perna_d', (-0.12, 0, 0.35), (-0.13, 0, 0.0), 'raiz')])
    B.prende(cilindro('lata', (0, 0, 0.82), 0.3, 0.92, LATA, sub=0), 'corpo')
    B.prende(cilindro('tampa', (0, 0, 1.3), 0.27, 0.04, PRATA), 'corpo'); B.prende(cilindro('fundo', (0, 0, 0.35), 0.27, 0.04, PRATA), 'corpo')
    B.prende(cilindro('anel', (0, -0.08, 1.33), 0.07, 0.015, PRATA, rot=(0, 0, 0)), 'corpo')
    B.prende(caixa('faixa', (0, -0.25, 0.68), (0.2, 0.06, 0.07), mat('faixa_lata', '#ffffff', 0.3)), 'corpo')
    B.rosto('corpo', (0, -0.31, 1.02), 0.1, 0.08, boca=False)
    b = esfera('boca', (0, -0.31, 0.86), (0.07, 0.02, 0.03), mat('boca', '#5a1f2b', 0.4)); B.prende(b, 'corpo'); B.boca = b
    _bracos_pernas(B, (0.29, 0, 0.85), (0.48, -0.05, 0.55), (0.12, 0, 0.36), (0.13, 0, 0.0), 0.04, 0.045, PRATA, PRATA, PRATA, mat('tenis', '#ffffff', 0.5))
    return B

def saco(nome, cor):
    """saco de lixo estufado, plástico brilhante, com o nó em cima"""
    SAC = mat('saco_' + nome, cor, 0.22)
    B = Boneco(nome, [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 0.3), (0, 0, 1.3), 'raiz'), ('no', (0, 0, 1.3), (0, 0, 1.75), 'corpo'),
                      ('braco_e', (0.48, 0, 0.8), (0.72, -0.05, 0.5), 'corpo'), ('braco_d', (-0.48, 0, 0.8), (-0.72, -0.05, 0.5), 'corpo'),
                      ('perna_e', (0.2, 0, 0.25), (0.2, 0, 0.0), 'raiz'), ('perna_d', (-0.2, 0, 0.25), (-0.2, 0, 0.0), 'raiz')])
    o = esfera('saco', (0, 0, 0.72), (0.55, 0.48, 0.62), SAC, 2)
    tx = bpy.data.textures.new('amassado_' + nome, 'CLOUDS'); tx.noise_scale = 0.35
    d = o.modifiers.new('amassado', 'DISPLACE'); d.texture = tx; d.strength = 0.08
    o.modifiers.move(1, 0); B.prende(o, 'corpo')
    bpy.ops.mesh.primitive_cone_add(radius1=0.16, radius2=0.04, depth=0.3, location=(0, 0, 1.38), vertices=24)
    c = bpy.context.object; c.name = 'pescoco_saco'; c.data.materials.append(SAC); _liso(c, 1); B.prende(c, 'no')
    for lado in (1, -1): B.prende(membro('ponta', (0.02 * lado, 0, 1.52), (0.2 * lado, -0.02, 1.68), 0.06, SAC), 'no')
    B.rosto('corpo', (0, -0.45, 0.9), 0.15, 0.1, boca=False)
    b = esfera('boca', (0, -0.5, 0.68), (0.1, 0.03, 0.04), mat('boca', '#5a1f2b', 0.4)); B.prende(b, 'corpo'); B.boca = b
    _bracos_pernas(B, (0.48, 0, 0.8), (0.7, -0.05, 0.52), (0.2, 0, 0.25), (0.2, 0, 0.0), 0.06, 0.07, SAC, SAC, SAC, SAC)
    return B

def chuva():
    """nuvem de chuva brava, com gotas penduradas"""
    NUV, GOTA = mat('nuvem', '#7d8799', 0.9), mat('gota', '#6fb7ff', 0.05, 0.3, 0.6)
    B = Boneco('Chuva', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 1.4), (0, 0, 2.6), 'raiz'),
                         ('braco_e', (0.8, 0, 1.9), (1.1, -0.05, 1.5), 'corpo'), ('braco_d', (-0.8, 0, 1.9), (-1.1, -0.05, 1.5), 'corpo')])
    for (x, z, r) in ((0, 2.1, 0.62), (-0.55, 1.95, 0.45), (0.55, 1.95, 0.48), (-0.3, 2.45, 0.42), (0.32, 2.42, 0.4), (-0.9, 1.85, 0.3), (0.92, 1.88, 0.3)):
        B.prende(esfera('nuvem', (x, 0, z), (r, r * 0.8, r * 0.85), NUV), 'corpo')
    B.rosto('corpo', (0, -0.5, 2.1), 0.2, 0.12, boca=False, sobr=mat('sobr_nuvem', '#3c4250', 0.8))
    b = esfera('boca', (0, -0.52, 1.88), (0.14, 0.03, 0.05), mat('boca', '#5a1f2b', 0.4)); B.prende(b, 'corpo'); B.boca = b
    for k in range(9):
        x = -0.8 + k * 0.2; z = 1.3 - (k % 3) * 0.28
        B.prende(esfera('gota', (x, -0.05, z), (0.05, 0.05, 0.09), GOTA, 1), 'corpo')
    for lado, s in ((1, 'e'), (-1, 'd')):
        B.prende(membro('braco', (0.8 * lado, 0, 1.9), (1.08 * lado, -0.05, 1.55), 0.08, NUV), 'braco_' + s)
        B.prende(esfera('mao', (1.1 * lado, -0.05, 1.48), (0.1, 0.1, 0.1), NUV), 'braco_' + s)
    return B

def rio():
    """o Rio: corpo de água azul com crista de onda, calmo e sábio"""
    AGUA, ESPUMA = mat('agua', '#2f86c9', 0.08, 0.0, 0.25), mat('espuma', '#dff3ff', 0.4)
    B = Boneco('Rio', [('raiz', (0, 0, 0), (0, 0, 0.3), None), ('corpo', (0, 0, 0.3), (0, 0, 1.6), 'raiz'), ('cabeca', (0, 0, 1.6), (0, 0, 2.3), 'corpo'),
                       ('braco_e', (0.55, 0, 1.3), (0.85, -0.05, 0.85), 'corpo'), ('braco_d', (-0.55, 0, 1.3), (-0.85, -0.05, 0.85), 'corpo')])
    B.prende(esfera('base', (0, 0, 0.35), (0.85, 0.6, 0.4), AGUA), 'raiz')
    B.prende(esfera('corpo', (0, 0, 1.15), (0.58, 0.45, 0.75), AGUA), 'corpo')
    B.prende(esfera('cabeca', (0, -0.02, 1.9), (0.45, 0.4, 0.42), AGUA), 'cabeca')
    for (x, z, r) in ((-0.3, 2.3, 0.18), (0.0, 2.38, 0.22), (0.3, 2.3, 0.18), (0.48, 2.18, 0.13)):
        B.prende(esfera('crista', (x, 0.05, z), (r, r * 0.8, r * 0.7), ESPUMA), 'cabeca')
    for (x, r) in ((-0.6, 0.12), (-0.2, 0.1), (0.25, 0.11), (0.62, 0.12)): B.prende(esfera('espuma', (x, -0.35, 0.12), (r, r, r * 0.6), ESPUMA), 'raiz')
    B.rosto('cabeca', (0, -0.36, 1.98), 0.15, 0.1, boca=False)
    b = esfera('boca', (0, -0.42, 1.74), (0.11, 0.03, 0.04), mat('boca', '#103a5c', 0.4)); B.prende(b, 'cabeca'); B.boca = b
    for lado, s in ((1, 'e'), (-1, 'd')):
        B.prende(membro('braco', (0.55 * lado, 0, 1.3), (0.85 * lado, -0.05, 0.9), 0.1, AGUA), 'braco_' + s)
        B.prende(esfera('mao', (0.87 * lado, -0.05, 0.82), (0.11, 0.11, 0.11), ESPUMA), 'braco_' + s)
    return B

def elenco():
    """todos os personagens do livro, cada um com o seu jeito"""
    return {
        'Rato': rato(),
        'Latinha': latinha(),
        'Saco de lixo I': saco('Saco de lixo I', '#1f4fa8'),       # azul
        'Saco de lixo II': saco('Saco de lixo II', '#24242a'),     # preto
        'Mulher': pessoa('Mulher', 2.35, '#e7b08c', '#7a3b1a', 'longo', '#d9579a', '#000000', saia='#7c4fb0', sapato='#8a2040', sujo=True),
        'Marido': pessoa('Marido', 2.55, '#c98e66', '#2b1a10', 'curto', '#3f8f5a', '#3b4766', sujo=True),
        'Garoto': pessoa('Garoto', 1.75, '#9a6a4a', '#1a120c', 'bone', '#f2c230', '#3a64b8', sapato='#ffffff'),
        'Mãe': pessoa('Mãe', 2.35, '#f0c4a0', '#3a2414', 'coque', '#3aa6a0', '#000000', saia='#e0884a', sapato='#5a3a20'),
        'Chuva': chuva(),
        'Rio': rio(),
    }
