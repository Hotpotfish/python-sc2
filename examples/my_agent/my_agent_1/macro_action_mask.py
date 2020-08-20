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
    if self.supply_cap < 200 and self.supply_left < 10:
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


async def buildBarracksReactor_mask(self):
    for Barracks in self.structures(UnitTypeId.BARRACKS).ready:
        if not Barracks.has_add_on and self.can_afford(UnitTypeId.BARRACKSREACTOR):
            addon_points = points_to_build_addon(Barracks.position)
            if all(
                    self.in_map_bounds(addon_point)
                    and self.in_placement_grid(addon_point)
                    and self.in_pathing_grid(addon_point)
                    for addon_point in addon_points
            ):
                return 1
    return 0


async def liftBarracks_mask(self):
    if self.structures(UnitTypeId.BARRACKS):
        if self.structures(UnitTypeId.BARRACKS).idle:
            return 1
    return 0


async def landAndBuildBarracksReactor_mask(self):
    if self.structures(UnitTypeId.BARRACKSFLYING):
        if self.structures(UnitTypeId.BARRACKSFLYING).idle:
            if self.can_afford(UnitTypeId.BARRACKSREACTOR):
                for Barracks in self.structures(UnitTypeId.BARRACKSFLYING).idle:
                    possible_land_positions_offset = sorted(
                        (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                        key=lambda point: point.x ** 2 + point.y ** 2,
                    )
                    offset_point: Point2 = Point2((-0.5, -0.5))
                    possible_land_positions = (Barracks.position.rounded + offset_point + p for p in possible_land_positions_offset)
                    for target_land_position in possible_land_positions:
                        land_and_addon_points: List[Point2] = land_positions(target_land_position)
                        if all(
                                self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos) and self.in_pathing_grid(land_pos)
                                for land_pos in land_and_addon_points
                        ):
                            Barracks(AbilityId.LAND, target_land_position)
                            return 1
    return 0


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
            if CCs and len(self.units(UnitTypeId.SCV)) < 22 * len(CCs):
                for cc in CCs:
                    if cc.is_idle:
                        # cc.train(UnitTypeId.SCV)
                        return 1
    return 0


# 训练枪兵（至少一个）
async def trainMarine_mask(self):
    if self.structures(UnitTypeId.BARRACKS):
        if self.structures(UnitTypeId.BARRACKS).ready:
            # for barracks in self.structures(UnitTypeId.BARRACKS).ready:
            if self.can_afford(UnitTypeId.MARINE):
                if self.supply_left >= 0:
                    # barracks.train(UnitTypeId.MARINE)
                    return 1
    return 0


# 训练暴风（至少一个）
async def trainHellion_mask(self):
    if self.structures(UnitTypeId.FACTORY):
        if self.structures(UnitTypeId.FACTORY).ready:
            if self.can_afford(UnitTypeId.HELLION):
                if self.supply_left >= 2:
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


async def detectionAndAttack_mask(self):
    if self.mineral_field:
        if not self.enemy_structures:
            if not self.enemy_units:
                if self.supply_army > 0:
                    return 1
    return 0


async def massNearEnemyBase_mask(self):
    if self.enemy_structures:
        if self.supply_army > 10:
            return 1
    return 0


async def massNearBase_mask(self):
    if self.townhalls():
        if self.supply_army > 10:
            return 1
    return 0


async def retreat_mask(self):
    if self.townhalls():
        if self.supply_army < 10:
            return 1
    return 0


async def defence_mask(self):
    if self.supply_army > 0:
        if self.structures:
            if self.enemy_units:
                # close_enemy = self.enemy_units.closest_to(self.structures)
                enemy_units = next((unit for unit in self.enemy_units), None)
                if self.structures.closest_distance_to(enemy_units) < 10:
                    return 1
    return 0


async def attackEnemySquad_mask(self):
    if self.supply_army > 20:
        if self.enemy_units:
            return 1
    return 0


async def attackNearestBase_mask(self):
    if self.enemy_structures:
        if self.structures:
            if self.supply_army > 10:
                return 1
    return 0


async def getMask(self):
    mask = []
    a_length = len(economic_action)
    for i in range(a_length):
        if economic_action[i] == doNothing:
            mask.append(1)
        if economic_action[i] == buildSupplydepot:
            mask.append(await buildSupplydepot_mask(self))

        if economic_action[i] == buildBarracksReactor:
            mask.append(await buildBarracksReactor_mask(self))
        if economic_action[i] == buildBarracks:
            mask.append(await buildBarracks_mask(self))
        if economic_action[i] == liftBarracks:
            mask.append(await liftBarracks_mask(self))
        if economic_action[i] == landAndBuildBarracksReactor:
            mask.append(await landAndBuildBarracksReactor_mask(self))

        if economic_action[i] == buildRefinery:
            mask.append(await buildRefinery_mask(self))
        if economic_action[i] == buildFactory:
            mask.append(await buildFactory_mask(self))
        if economic_action[i] == expand:
            mask.append(await expand_mask(self))
        if economic_action[i] == trainScv:
            mask.append(await trainScv_mask(self))
        if economic_action[i] == trainMarine:
            mask.append(await trainMarine_mask(self))
        if economic_action[i] == trainHellion:
            mask.append(await trainHellion_mask(self))
        if economic_action[i] == scvBackToMineral:
            mask.append(await scvBackToMineral_mask(self))
        if economic_action[i] == scvBackToRefinery:
            mask.append(await scvBackToRefinery_mask(self))
        if economic_action[i] == detectionAndAttack:
            mask.append(await detectionAndAttack_mask(self))
        if economic_action[i] == massNearEnemyBase:
            mask.append(await massNearEnemyBase_mask(self))
        if economic_action[i] == massNearBase:
            mask.append(await massNearBase_mask(self))
        if economic_action[i] == retreat:
            mask.append(await retreat_mask(self))
        if economic_action[i] == defence:
            mask.append(await defence_mask(self))
        if economic_action[i] == attackEnemySquad:
            mask.append(await attackEnemySquad_mask(self))
        if economic_action[i] == attackNearestBase:
            mask.append(await attackNearestBase_mask(self))
    return mask
