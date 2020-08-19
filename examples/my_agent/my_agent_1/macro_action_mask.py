import random

from examples.my_agent.my_agent_1.action_list import *
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.units import Units
from sc2.unit import Unit

TRAIN_NUMBER = 2


# 动作若无法执行直接输出no-op

# 修建补给站
async def buildSupplydepot_mask(self):
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
                        return 1
    return 0


# 修建兵营
async def buildBarracks_mask(self):
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
                            return 1
    return 0


# 修建瓦斯矿场
async def buildRefinery_mask(self):
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
                        return 1
    return 0


# 修建重工厂
async def buildFactory_mask(self):
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
                            return 1
    return 0


async def expand_mask(self):
    if self.can_afford(UnitTypeId.COMMANDCENTER):
        return 1
    return 0


async def trainScv_mask(self):
    if self.can_afford(UnitTypeId.SCV):
        if self.supply_left > 0:
            CCs: Units = self.townhalls()
            if CCs:
                for cc in CCs:
                    if cc.is_idle:
                        # cc.train(UnitTypeId.SCV)
                        return 1
    return 0


# 训练枪兵（至少一个）
async def trainMarine_mask(self):
    if self.structures(UnitTypeId.BARRACKS):
        if self.structures(UnitTypeId.BARRACKS).ready.idle:
            # for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if self.can_afford(UnitTypeId.MARINE):
                if self.supply_left > 0:
                    # barracks.train(UnitTypeId.MARINE)
                    return 1
    return 0


# 训练暴风（至少一个）
async def trainHellion_mask(self):
    if self.structures(UnitTypeId.FACTORY):
        if self.structures(UnitTypeId.FACTORY).ready.idle:
            if self.can_afford(UnitTypeId.HELLION):
                if self.supply_left > 2:
                    # factory.train(UnitTypeId.HELLION)
                    return 1
    return 0


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


# 回去采矿（至少一个生效）
async def scvBackToMineral_mask(self):
    if self.workers.idle:
        for scv in self.workers.idle:
            if self.townhalls():
                cc: Units = self.townhalls().closest_to(scv)
                if cc:
                    mineral_field_close = self.mineral_field.closest_to(cc)
                    if mineral_field_close:
                        if mineral_field_close.assigned_harvesters < mineral_field_close.ideal_harvesters:
                            # worker: Units = self.workers.closer_than(10, refinery)
                            return 1
    return 0

    # scv.gather(self.mineral_field.closest_to(cc))


# 回去采瓦斯（至少一个生效）
async def scvBackToRefinery_mask(self):
    if self.gas_buildings:
        for refinery in self.gas_buildings:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker: Units = self.workers.closer_than(10, refinery)
                if worker:
                    return 1
    return 0


# 枪兵攻击敌人
async def marineAttack_mask(self):
    forces: Units = self.units(UnitTypeId.MARINE)
    if forces:
        return 1
    return 0


async def hellionAttack_mask(self):
    forces: Units = self.units(UnitTypeId.HELLION)
    if forces:
        return 1
    return 0


async def getMask(self):
    mask = []
    a_length = len(economic_action)
    for i in range(a_length):
        if economic_action[i] == buildSupplydepot:
            mask.append(buildSupplydepot_mask(self))
        if economic_action[i] == buildBarracks:
            mask.append(buildBarracks_mask(self))
        if economic_action[i] == buildRefinery:
            mask.append(buildRefinery_mask(self))
        if economic_action[i] == buildFactory:
            mask.append(buildFactory_mask(self))
        if economic_action[i] == expand:
            mask.append(expand_mask(self))
        if economic_action[i] == trainScv:
            mask.append(trainScv_mask(self))
        if economic_action[i] == trainMarine:
            mask.append(trainMarine_mask(self))
        if economic_action[i] == trainHellion:
            mask.append(trainHellion_mask(self))
        if economic_action[i] == scvBackToMineral:
            mask.append(scvBackToMineral_mask(self))
        if economic_action[i] == scvBackToRefinery:
            mask.append(scvBackToRefinery_mask(self))
        if economic_action[i] == marineAttack:
            mask.append(marineAttack_mask(self))
        if economic_action[i] == hellionAttack:
            mask.append(hellionAttack_mask(self))
