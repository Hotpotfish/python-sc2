import random
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.units import Units
from sc2.unit import Unit


# 动作若无法执行直接输出no-op

# 修建补给站
async def buildSupplydepot(self):
    # 是否能承担

    if self.can_afford(UnitTypeId.SUPPLYDEPOT):
        CCs: Units = self.townhalls()
        # 指挥中心是否还在
        if CCs:
            worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
            # 是否有空闲工人
            if worker_candidates:
                for cc in CCs:
                    map_center = self.game_info.map_center
                    position_towards_map_center = cc.position.towards(map_center, distance=8)
                    placement_position = await self.find_placement(UnitTypeId.SUPPLYDEPOT, near=position_towards_map_center)
                    # Placement_position can be None
                    # 是否有合适的位置
                    if placement_position:
                        build_worker = worker_candidates.closest_to(placement_position)
                        build_worker.build(UnitTypeId.SUPPLYDEPOT, placement_position)
                        # return


# 修建兵营
async def buildBarracks(self):
    # 是否能承担
    if self.can_afford(UnitTypeId.BARRACKS):
        # 科技树依赖
        if self.structures(UnitTypeId.SUPPLYDEPOT) or self.structures(UnitTypeId.SUPPLYDEPOTLOWERED):
            CCs: Units = self.townhalls()
            # 指挥中心是否还在
            if CCs:
                worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                # 是否有空闲工人
                if worker_candidates:
                    for cc in CCs:
                        map_center = self.game_info.map_center
                        position_towards_map_center = cc.position.towards(map_center, distance=8)
                        placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=position_towards_map_center)
                        # Placement_position can be None
                        # 是否有合适的位置
                        if placement_position:
                            build_worker = worker_candidates.closest_to(placement_position)
                            build_worker.build(UnitTypeId.BARRACKS, placement_position)
                            return


# 修建瓦斯矿场
async def buildRefinery(self):
    # 是否能承担
    if self.can_afford(UnitTypeId.REFINERY):
        CCs: Units = self.townhalls()
        # 指挥中心是否还在
        if CCs:
            worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
            # 是否有空闲工人
            if worker_candidates:
                for cc in CCs:
                    vgs = self.vespene_geyser.closer_than(10, cc)
                    for vg in vgs:
                        if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
                            continue
                        # 是否有合适的位置
                        build_worker = worker_candidates.closest_to(vg)
                        build_worker.build_gas(vg)
                        return


# 修建重工厂
async def buildFactory(self):
    # 是否能承担
    if self.can_afford(UnitTypeId.FACTORY):
        # 科技树依赖
        if self.structures(UnitTypeId.SUPPLYDEPOT) or self.structures(UnitTypeId.BARRACKS):
            CCs: Units = self.townhalls()
            # 指挥中心是否还在
            if CCs:
                worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                # 是否有空闲工人
                if worker_candidates:
                    for cc in CCs:
                        map_center = self.game_info.map_center
                        position_towards_map_center = cc.position.towards(map_center, distance=8)
                        placement_position = await self.find_placement(UnitTypeId.FACTORY, near=position_towards_map_center)
                        # Placement_position can be None
                        # 是否有合适的位置
                        if placement_position:
                            build_worker = worker_candidates.closest_to(placement_position)
                            build_worker.build(UnitTypeId.FACTORY, placement_position)
                            return


async def expand(self):
    if self.can_afford(UnitTypeId.COMMANDCENTER):
        await self.expand_now()


async def trainScv(self):
    if self.can_afford(UnitTypeId.SCV):
        if self.supply_left > 0:
            CCs: Units = self.townhalls()
            if CCs:
                for cc in CCs:
                    if cc.is_idle:
                        cc.train(UnitTypeId.SCV)
                        return


# 训练枪兵（至少一个）
async def trainMarine(self):
    if self.structures(UnitTypeId.BARRACKS):
        for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if self.can_afford(UnitTypeId.MARINE):
                if self.supply_left > 0:
                    barracks.train(UnitTypeId.MARINE)


# 训练暴风（至少一个）
async def trainHellion(self):
    if self.structures(UnitTypeId.FACTORY):
        for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
            if self.can_afford(UnitTypeId.HELLION):
                if self.supply_left > 2:
                    factory.train(UnitTypeId.HELLION)


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


# 回去采矿
async def scvBackToMineral(self):
    if self.workers.idle:
        for scv in self.workers.idle:
            if self.townhalls():
                cc: Units = self.townhalls().closest_to(scv)
                if cc:
                    mineral_field_close = self.mineral_field.closest_to(cc)
                    if mineral_field_close:
                        if mineral_field_close.assigned_harvesters < mineral_field_close.ideal_harvesters:
                            # worker: Units = self.workers.closer_than(10, refinery)
                            scv.gather(mineral_field_close)

        # scv.gather(self.mineral_field.closest_to(cc))


# 回去采瓦斯
async def scvBackToRefinery(self):
    if self.gas_buildings:
        for refinery in self.gas_buildings:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker: Units = self.workers.closer_than(10, refinery)
                if worker:
                    worker.random.gather(refinery)


# 枪兵攻击敌人
async def marineAttack(self):
    target: Point2 = select_target(self)
    forces: Units = self.units(UnitTypeId.MARINE)
    for unit in forces:
        unit.attack(target)


async def hellionAttack(self):
    target: Point2 = select_target(self)
    forces: Units = self.units(UnitTypeId.HELLION)
    for unit in forces:
        unit.attack(target)
