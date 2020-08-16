import random
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.units import Units
from sc2.unit import Unit


# 动作不进行合法性检测

# 修建补给站
async def buildSupplydepot(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8))


# 修建兵营
async def buildBarracks(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 8))


# 修建瓦斯矿场
async def buildRefinery(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    vgs = self.vespene_geyser.closer_than(10, cc)
    for vg in vgs:
        # if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
        #     continue
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


# 修建重工厂
async def buildFactory(self):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    vgs = self.vespene_geyser.closer_than(10, cc)
    for vg in vgs:
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


# 训练枪兵（至少一个）
async def trainMarine(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
        # Reactor allows us to build two at a time
        if self.can_afford(UnitTypeId.MARINE):
            barracks.train(UnitTypeId.MARINE)
        else:
            break


def select_target(self) -> Point2:
    # Pick a random enemy structure's position
    targets = self.enemy_structures
    if targets:
        return targets.random.position

    # Pick a random enemy unit's position
    targets = self.enemy_units
    if targets:
        return targets.random.position

    # Pick enemy start location if it has no friendly units nearby
    if min([unit.distance_to(self.enemy_start_locations[0]) for unit in self.units]) > 5:
        return self.enemy_start_locations[0]

    # Pick a random mineral field on the map
    return self.mineral_field.random.position


async def marineAttack(self):
    target: Point2 = self.select_target()
    forces: Units = self.units(UnitTypeId.MARINE)
    for unit in forces:
        unit.attack(target)
