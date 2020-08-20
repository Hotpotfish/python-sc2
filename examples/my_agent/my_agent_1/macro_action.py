import random

from sc2 import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.units import Units
from sc2.unit import Unit
from typing import Tuple, List
from sklearn.cluster import k_means
from sklearn.cluster import KMeans


# 动作若无法执行直接输出no-op
async def doNothing(self):
    return


# 修建补给站
async def buildSupplydepot(self):
    # a = Point2((3,1))
    # 是否能承担
    CCs: Units = self.townhalls()
    # 指挥中心是否还在
    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
    # 是否有空闲工人
    for cc in CCs:
        map_center = self.game_info.map_center
        position_towards_map_center = cc.position.towards(map_center, distance=8)
        placement_position = await self.find_placement(UnitTypeId.SUPPLYDEPOT, near=position_towards_map_center)
        # Placement_position can be None
        # 是否有合适的位置
        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.SUPPLYDEPOT, placement_position)
        return
        # return


# 修建兵营
async def buildBarracks(self):
    # 是否能承担

    # 科技树依赖

    CCs: Units = self.townhalls()

    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
    # 是否有空闲工人
    for cc in CCs:
        map_center = self.game_info.map_center
        position_towards_map_center = cc.position.towards(map_center, distance=8)
        placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=position_towards_map_center)
        # Placement_position can be None
        # 是否有合适的位置
        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.BARRACKS, placement_position)
        return


def points_to_build_addon(sp_position: Point2) -> List[Point2]:
    """ Return all points that need to be checked when trying to build an addon. Returns 4 points. """
    addon_offset: Point2 = Point2((2.5, -0.5))
    addon_position: Point2 = sp_position + addon_offset
    addon_points = [
        (addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)
    ]
    return addon_points


async def buildBarracksReactor(self):
    for Barracks in self.structures(UnitTypeId.BARRACKS).ready:
        if not Barracks.has_add_on:
            addon_points = points_to_build_addon(Barracks.position)
            if all(
                    self.in_map_bounds(addon_point)
                    and self.in_placement_grid(addon_point)
                    and self.in_pathing_grid(addon_point)
                    for addon_point in addon_points
            ):
                Barracks.build(UnitTypeId.BARRACKSREACTOR)


async def liftBarracks(self):
    for Barracks in self.structures(UnitTypeId.BARRACKS).idle:
        if not Barracks.has_add_on:
            Barracks(AbilityId.LIFT)
            return


def land_positions(sp_position: Point2) -> List[Point2]:
    """ Return all points that need to be checked when trying to land at a location where there is enough space to build an addon. Returns 13 points. """
    land_positions = [(sp_position + Point2((x, y))).rounded for x in range(-1, 2) for y in range(-1, 2)]
    return land_positions + points_to_build_addon(sp_position)


async def landAndBuildBarracksReactor(self):
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
                return


# 修建瓦斯矿场
async def buildRefinery(self):
    CCs: Units = self.townhalls()
    # 指挥中心是否还在

    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
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
    CCs: Units = self.townhalls()
    # 指挥中心是否还在
    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
    # 是否有空闲工人
    for cc in CCs:
        map_center = self.game_info.map_center
        position_towards_map_center = cc.position.towards(map_center, distance=8)
        placement_position = await self.find_placement(UnitTypeId.FACTORY, near=position_towards_map_center)
        # Placement_position can be None
        # 是否有合适的位置
        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.FACTORY, placement_position)
        return


async def expand(self):
    await self.expand_now()


async def trainScv(self):
    CCs: Units = self.townhalls()
    for cc in CCs:
        cc.train(UnitTypeId.SCV)
        return


# 训练枪兵（至少一个）
async def trainMarine(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.MARINE)
        return


async def trainMarauder(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.Marauder)
        return


async def trainHellion(self):
    for factory in self.structures(UnitTypeId.FACTORY).ready:
        factory.train(UnitTypeId.HELLION)
        return


async def trainGhost(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.GHOST)
        return


async def trainViking(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.VIKING)
        return


async def trainThor(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.THOR)
        return


async def trainRaven(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.RAVEN)
        return


async def trainBanshee(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.BANSHEE)
        return


async def trainWidowmine(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.WIDOWMINE)
        return


async def trainLiberator(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.LIBERATOR)
        return


async def trainCyclone(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.CYCLON)
        return


async def trainBattlecruiser(self):
    for barracks in self.structures(UnitTypeId.BARRACKS).ready:
        barracks.train(UnitTypeId.BATTLECRUISER)
        return


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
    for scv in self.workers.idle:
        cc: Units = self.townhalls().closest_to(scv)
        mineral_field_close = self.mineral_field.closest_to(cc)
        if mineral_field_close.assigned_harvesters < mineral_field_close.ideal_harvesters:
            # worker: Units = self.workers.closer_than(10, refinery)
            scv.gather(mineral_field_close)
            return

            # scv.gather(self.mineral_field.closest_to(cc))


# 回去采瓦斯
async def scvBackToRefinery(self):
    for refinery in self.gas_buildings:
        if refinery.assigned_harvesters < refinery.ideal_harvesters:
            worker: Units = self.workers.closer_than(10, refinery)
            if worker:
                worker.random.gather(refinery)
                return
            # 枪兵攻击敌人


# 攻击任意一个矿点
async def detectionAndAttack(self):
    forces: Units = self.units
    for unit in forces:
        if unit.type_id == UnitTypeId.SCV:
            continue
        unit.attack(self.mineral_field.random.position)


async def massNearEnemyBase(self):
    if self.enemy_structures(UnitTypeId.COMMANDCENTER):
        eCCs = self.enemy_structures(UnitTypeId.COMMANDCENTER)
        cc: Unit = eCCs.random

        map_center = self.game_info.map_center
        position_towards_map_center = cc.position.towards(map_center, distance=30)
        forces: Units = self.units
        for unit in forces:
            if unit.type_id == UnitTypeId.SCV:
                continue
            unit.attack(position_towards_map_center)
    else:
        enemy_structure_Nearest = self.enemy_structures.in_closest_distance_to_group(self.structures)
        # targets = self.enemy_structures
        map_center = self.game_info.map_center
        position_towards_map_center = enemy_structure_Nearest.position.towards(map_center, distance=20)
        forces: Units = self.units
        for unit in forces:
            if unit.type_id == UnitTypeId.SCV:
                continue
            unit.attack(position_towards_map_center)


async def massNearBase(self):
    CCs = self.townhalls()
    cc: Unit = CCs.random
    map_center = self.game_info.map_center
    position_towards_map_center = cc.position.towards(map_center, distance=15)
    forces: Units = self.units
    for unit in forces:
        if unit.type_id == UnitTypeId.SCV:
            continue
        unit.move(position_towards_map_center)


async def retreat(self):
    CCs = self.townhalls()
    cc: Unit = CCs.random
    map_center = self.game_info.map_center
    position_towards_map_center = cc.position.towards(map_center, distance=10)
    forces: Units = self.units
    for unit in forces:
        if unit.type_id == UnitTypeId.SCV:
            continue
        unit.move(position_towards_map_center)


async def defence(self):
    structures = next((structures for structures in self.structures), None)
    close_enemy = self.enemy_units.closest_to(structures)
    forces: Units = self.units
    for unit in forces:
        if unit.type_id == UnitTypeId.SCV:
            continue
        unit.attack(close_enemy.position)


def getMaxNum(arry):
    temparry = {}  # 保存处理后的数据
    times = 0  # 保存最高的那个次数
    for i in arry:
        if (temparry.get(i) == None):  # 若值为空
            # temparry追加一个元素
            temparry.setdefault(i, 1)
        else:
            temparry[i] += 1  # 键对应的值+1
    for k, v in temparry.items():
        if v > times:
            times = v
    return [k for k, v in temparry.items() if v == times]


async def attackEnemySquad(self):
    if len(self.enemy_units) > 3:
        enemy_coordinates = [[enemy.position.x, enemy.position.y] for enemy in self.enemy_units]
        keams_ememy = KMeans(n_clusters=3, random_state=0).fit(enemy_coordinates)
        squad = getMaxNum(keams_ememy.labels_)[0]
        position = Point2(keams_ememy.cluster_centers_[squad])
        forces: Units = self.units
        for unit in forces:
            if unit.type_id == UnitTypeId.SCV:
                continue
            unit.attack(position)
    else:
        targets = self.enemy_units
        if targets:
            return targets.random.position


async def attackNearestBase(self):
    enemy_structure_Nearest = self.enemy_structures.in_closest_distance_to_group(self.structures)
    # target: Point2 = select_target(self)
    forces: Units = self.units
    for unit in forces:
        if unit.type_id == UnitTypeId.SCV:
            continue
        unit.attack(enemy_structure_Nearest.position)
