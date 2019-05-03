# import decimal
# from FinishSurfaces.models import (
#     FinishSurface,
#     Finish,
#     Look,
#     Edge,
#     Material,
#     ShadeVariation,
#     SurfaceCoating,
#     SubMaterial
# )


# def add_finish_surface(row):
#     material_label = row['material_label']
#     sub_material_label = row['sub_material_label']
#     look_label = row['look_label']
#     finish_label = row['finish_label']
#     gloss_level = row['gloss_level']
#     texture_label = row['texture_label']
#     thickness = row['thickness']
#     try:
#         thickness = decimal.Decimal(thickness)
#     except:
#         thickness = None
#     length = row['length']
#     width = row['width']

#     lrv = row['lrv']
#     cof = row['cof']
#     # wet_cof = row['wet_cof']

#     # generic_color = row['generic_color']
#     shade = row['shade']
#     shade_variation = row['shade_variation']

#     edge = row['edge']
#     # end = row['end']

#     # rating_value = row['rating_value']
#     # rating_count = row['rating_count']

#     install_type = row['install_type']
#     sqft_per_carton = row['sqft_per_carton']
#     # weight_per_carton = row['weight_per_carton']
#     # recommended_grout = row['recommended_grout']
#     notes = row['notes']

#     slip_resistance = row['slip_resistance']

#     walls = row['walls']
#     countertops = row['countertops']
#     floors = row['floors']
#     cabinet_fronts = row['cabinet_fronts']
#     shower_floors = row['shower_floors']
#     shower_walls = row['shower_walls']
#     exterior_walls = row['exterior_walls']
#     exterior_floors = row['exterior_floors']
#     covered_walls = row['covered_walls']
#     covered_floors = row['covered_floors']
#     pool_lining = row['pool_lining']

#     if not material_label:
#         return
#     material = Material.objects.get_or_create(label=material_label)[0]

#     finish_surface = FinishSurface()
#     finish_surface.material = material
#     finish_surface.slip_resistant = slip_resistance
#     finish_surface.install_type = install_type
#     finish_surface.sqft_per_carton = sqft_per_carton
#     finish_surface.lrv = lrv
#     finish_surface.cof = cof
#     finish_surface.notes = notes
#     finish_surface.shade = shade
#     finish_surface.thickness = thickness
#     finish_surface.length = length
#     finish_surface.width = width
#     finish_surface.walls = walls
#     finish_surface.floors = floors
#     finish_surface.countertops = countertops
#     finish_surface.cabinet_fronts = cabinet_fronts
#     finish_surface.shower_floors = shower_floors
#     finish_surface.shower_walls = shower_walls
#     finish_surface.exterior_walls = exterior_walls
#     finish_surface.exterior_floors = exterior_floors
#     finish_surface.covered_walls = covered_walls
#     finish_surface.covered_floors = covered_floors
#     finish_surface.pool_linings = pool_lining

#     if edge:
#         edge_obj = Edge.objects.get_or_create(label=edge)[0]
#         finish_surface.edge = edge_obj
#     if shade_variation:
#         shadvar = ShadeVariation.objects.get_or_create(label=shade_variation)[0]
#         finish_surface.shade_variation = shadvar
#     if look_label:
#         look = Look.objects.get_or_create(label=look_label)[0]
#         finish_surface.look = look
#     if sub_material_label:
#         sub_material = SubMaterial.objects.get_or_create(label=sub_material_label, material=material)[0]
#         finish_surface.sub_material = sub_material
#     if finish_label:
#         surface_coating = SurfaceCoating.objects.get_or_create(label=finish_label, material=material)[0]
#         finish_surface.surface_coating = surface_coating
#     if texture_label or gloss_level:
#         finish_holder = None
#         if texture_label:
#             finish_holder = texture_label
#         if gloss_level:
#             finish_holder = gloss_level
#         finish = Finish.objects.get_or_create(label=finish_holder, material=material)[0]
#         finish_surface.finish = finish
#     # finish_surface.product = product
#     finish_surface.save()
#     return finish_surface
