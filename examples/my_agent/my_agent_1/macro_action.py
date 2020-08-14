import random
from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units
from sc2.unit import Unit

async def buildSupplydepot(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8))

async def buildBarracks(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 8))

async def buildRefinery(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    vgs = self.vespene_geyser.closer_than(10, cc)
    for vg in vgs:
        if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
            continue
        # Select a worker closest to the vespene geysir
        worker: Unit = self.select_build_worker(vg)
        # Worker can be none in cases where all workers are dead
        # or 'select_build_worker' function only selects from workers which carry no minerals
        if worker is None:
            continue
        # Issue the build command to the worker, important: vg has to be a Unit, not a position
        worker.build_gas(vg)
        # # Only issue one build geysir command per frame
        # break











# async def buildSupplydepot(self):
#     if not self.townhalls:
#         # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
#         for worker in self.workers:
#             worker.attack(self.enemy_start_locations[0])
#         return
#     else:
#         nexus = self.townhalls.random
#
#     # Make probes until we have 16 total
#     if self.supply_workers < 16 and nexus.is_idle:
#         if self.can_afford(UnitTypeId.PROBE):
#             nexus.train(UnitTypeId.PROBE)
#
#     # If we have no pylon, build one near starting nexus
#     elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
#         if self.can_afford(UnitTypeId.PYLON):
#             await self.build(UnitTypeId.PYLON, near=nexus)
#
#     # If we have no forge, build one near the pylon that is closest to our starting nexus
#     elif not self.structures(UnitTypeId.FORGE):
#         pylon_ready = self.structures(UnitTypeId.PYLON).ready
#         if pylon_ready:
#             if self.can_afford(UnitTypeId.FORGE):
#                 await self.build(UnitTypeId.FORGE, near=pylon_ready.closest_to(nexus))
#
#     # If we have less than 2 pylons, build one at the enemy base
#     elif self.structures(UnitTypeId.PYLON).amount < 2:
#         if self.can_afford(UnitTypeId.PYLON):
#             pos = self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 15))
#             await self.build(UnitTypeId.PYLON, near=pos)
#
#     # If we have no cannons but at least 2 completed pylons, automatically find a placement location and build them near enemy start location
#     elif not self.structures(UnitTypeId.PHOTONCANNON):
#         if self.structures(UnitTypeId.PYLON).ready.amount >= 2 and self.can_afford(UnitTypeId.PHOTONCANNON):
#             pylon = self.structures(UnitTypeId.PYLON).closer_than(20, self.enemy_start_locations[0]).random
#             await self.build(UnitTypeId.PHOTONCANNON, near=pylon)
#
#     # Decide if we should make pylon or cannons, then build them at random location near enemy spawn
#     elif self.can_afford(UnitTypeId.PYLON) and self.can_afford(UnitTypeId.PHOTONCANNON):
#         # Ensure "fair" decision
#         for _ in range(20):
#             pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
#             building = UnitTypeId.PHOTONCANNON if self.state.psionic_matrix.covers(pos) else UnitTypeId.PYLON
#             await self.build(building, near=pos)
