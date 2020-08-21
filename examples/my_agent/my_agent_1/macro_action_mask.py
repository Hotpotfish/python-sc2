import random

from examples.my_agent.my_agent_1.action_list import *
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.units import Units
from sc2.unit import Unit

TRAIN_NUMBER = 2
ATTACK_FREQUENCY = 32
BUILD_FREQUENCY = 32


# 动作若无法执行直接输出no-op

# 修建补给站
async def buildSupplydepot_mask(self):
    # 是否能承担
    if self.state.game_loop % BUILD_FREQUENCY:
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
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.BARRACKS) and (len(self.structures(UnitTypeId.BARRACKS)) + len(self.structures(UnitTypeId.BARRACKS)) <= 3):
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
    if self.state.game_loop % BUILD_FREQUENCY:
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


async def buildBarracksTechlab_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        for Barracks in self.structures(UnitTypeId.BARRACKS).ready:
            if not Barracks.has_add_on and self.can_afford(UnitTypeId.BARRACKSTECHLAB):
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


async def landAndReadyToBuildBarracksAddOn_mask(self):
    if self.structures(UnitTypeId.BARRACKSFLYING):
        if self.structures(UnitTypeId.BARRACKSFLYING).idle:
            if self.can_afford(UnitTypeId.BARRACKSREACTOR) and self.can_afford(UnitTypeId.BARRACKSTECHLAB):
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


async def buildEngineeringbay_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.ENGINEERINGBAY) and len(self.structures(UnitTypeId.ENGINEERINGBAY)) < 2:
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
                            placement_position = await self.find_placement(UnitTypeId.ENGINEERINGBAY, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildRefinery_mask(self):
    # 是否能承担
    if self.state.game_loop % BUILD_FREQUENCY:
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
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.FACTORY) and (len(self.structures(UnitTypeId.FACTORY)) + len(self.structures(UnitTypeId.FACTORY)) <= 2):
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


async def buildFactoryReactor_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        for factory in self.structures(UnitTypeId.FACTORY).ready:
            if not factory.has_add_on and self.can_afford(UnitTypeId.FACTORYREACTOR):
                addon_points = points_to_build_addon(factory.position)
                if all(
                        self.in_map_bounds(addon_point)
                        and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point)
                        for addon_point in addon_points
                ):
                    return 1
    return 0


async def buildFactoryTechlab_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        for Factory in self.structures(UnitTypeId.FACTORY).ready:
            if not Factory.has_add_on and self.can_afford(UnitTypeId.FACTORYTECHLAB):
                addon_points = points_to_build_addon(Factory.position)
                if all(
                        self.in_map_bounds(addon_point)
                        and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point)
                        for addon_point in addon_points
                ):
                    return 1
    return 0


async def liftFactory_mask(self):
    if self.structures(UnitTypeId.FACTORY):
        if self.structures(UnitTypeId.FACTORY).idle:
            return 1
    return 0


async def landAndReadyToBuildFactoryAddOn_mask(self):
    if self.structures(UnitTypeId.FACTORYFLYING):
        if self.structures(UnitTypeId.FACTORYFLYING).idle:
            if self.can_afford(UnitTypeId.FACTORYREACTOR) and self.can_afford(UnitTypeId.FACTORYTECHLAB):
                for Factory in self.structures(UnitTypeId.FACTORYFLYING).idle:
                    possible_land_positions_offset = sorted(
                        (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                        key=lambda point: point.x ** 2 + point.y ** 2,
                    )
                    offset_point: Point2 = Point2((-0.5, -0.5))
                    possible_land_positions = (Factory.position.rounded + offset_point + p for p in possible_land_positions_offset)
                    for target_land_position in possible_land_positions:
                        land_and_addon_points: List[Point2] = land_positions(target_land_position)
                        if all(
                                self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos) and self.in_pathing_grid(land_pos)
                                for land_pos in land_and_addon_points
                        ):
                            Factory(AbilityId.LAND, target_land_position)
                            return 1
    return 0


async def buildGhostAcademy_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.GHOSTACADEMY) and not self.structures(UnitTypeId.GHOSTACADEMY) and not self.already_pending(UnitTypeId.GHOSTACADEMY):
            # 科技树依赖
            if (self.structures(UnitTypeId.SUPPLYDEPOT) or self.structures(UnitTypeId.SUPPLYDEPOTLOWERED)) and \
                    self.structures(UnitTypeId.BARRACKS or self.structures(UnitTypeId.BARRACKSFLYING)):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=8)
                            placement_position = await self.find_placement(UnitTypeId.GHOSTACADEMY, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildMissileturret_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.MISSILETURRET) and (len(self.structures(UnitTypeId.MISSILETURRET)) + len(self.structures(UnitTypeId.MISSILETURRET)) <= 1):
            # 科技树依赖
            if self.structures(UnitTypeId.ENGINEERINGBAY):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=10)
                            placement_position = await self.find_placement(UnitTypeId.MISSILETURRET, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildSensortower_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.SENSORTOWER) and (len(self.structures(UnitTypeId.SENSORTOWER)) + len(self.structures(UnitTypeId.MISSILETURRET)) <= 1):
            # 科技树依赖
            if self.structures(UnitTypeId.ENGINEERINGBAY):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=10)
                            placement_position = await self.find_placement(UnitTypeId.SENSORTOWER, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildBunker_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.BUNKER) and (len(self.structures(UnitTypeId.BUNKER)) + len(self.structures(UnitTypeId.BUNKER)) <= 1):
            # 科技树依赖
            if self.structures(UnitTypeId.BARRACKS):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=12)
                            placement_position = await self.find_placement(UnitTypeId.BUNKER, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildArmory_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.ARMORY) and (len(self.structures(UnitTypeId.ARMORY)) + len(self.structures(UnitTypeId.ARMORY)) <= 2):
            # 科技树依赖
            if (self.structures(UnitTypeId.BARRACKS) or self.structures(UnitTypeId.BARRACKSFLYING)) and \
                    (self.structures(UnitTypeId.FACTORY) or self.structures(UnitTypeId.FACTORYFLYING)):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=9)
                            placement_position = await self.find_placement(UnitTypeId.ARMORY, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildFusioncore_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.FUSIONCORE) and (len(self.structures(UnitTypeId.FUSIONCORE)) + len(self.structures(UnitTypeId.FUSIONCORE)) <= 1):
            # 科技树依赖
            if (self.structures(UnitTypeId.SUPPLYDEPOT) or self.structures(UnitTypeId.SUPPLYDEPOTLOWERED)) and \
                    (self.structures(UnitTypeId.BARRACKS) or self.structures(UnitTypeId.BARRACKSFLYING)) and \
                    (self.structures(UnitTypeId.FACTORY) or self.structures(UnitTypeId.FACTORYFLYING)) and \
                    (self.structures(UnitTypeId.STARPORT) or self.structures(UnitTypeId.STARPORTFLYING)):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=9)
                            placement_position = await self.find_placement(UnitTypeId.FUSIONCORE, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildStarport_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        # 是否能承担
        if self.can_afford(UnitTypeId.STARPORT) and (len(self.structures(UnitTypeId.STARPORT)) + len(self.structures(UnitTypeId.STARPORT)) <= 2):
            # 科技树依赖
            if (self.structures(UnitTypeId.SUPPLYDEPOT) or self.structures(UnitTypeId.SUPPLYDEPOTLOWERED)) and \
                    (self.structures(UnitTypeId.BARRACKS) or self.structures(UnitTypeId.BARRACKSFLYING)) and \
                    (self.structures(UnitTypeId.FACTORY) or self.structures(UnitTypeId.FACTORYFLYING)):
                CCs: Units = self.townhalls()
                # 指挥中心是否还在
                if CCs:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # 是否有空闲工人
                    if worker_candidates:
                        for cc in CCs:
                            map_center = self.game_info.map_center
                            position_towards_map_center = cc.position.towards(map_center, distance=8)
                            placement_position = await self.find_placement(UnitTypeId.STARPORT, near=position_towards_map_center)
                            # Placement_position can be None
                            # 是否有合适的位置
                            if placement_position:
                                return 1
    return 0


async def buildStarportReactor_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        for Starport in self.structures(UnitTypeId.STARPORT).ready:
            if not Starport.has_add_on and self.can_afford(UnitTypeId.STARPORTREACTOR):
                addon_points = points_to_build_addon(Starport.position)
                if all(
                        self.in_map_bounds(addon_point)
                        and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point)
                        for addon_point in addon_points
                ):
                    return 1
    return 0


async def buildStarportTechlab_mask(self):
    if self.state.game_loop % BUILD_FREQUENCY:
        for Starport in self.structures(UnitTypeId.STARPORT).ready:
            if not Starport.has_add_on and self.can_afford(UnitTypeId.STARPORTTECHLAB):
                addon_points = points_to_build_addon(Starport.position)
                if all(
                        self.in_map_bounds(addon_point)
                        and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point)
                        for addon_point in addon_points
                ):
                    return 1
    return 0


async def liftStarport_mask(self):
    if self.structures(UnitTypeId.STARPORT):
        if self.structures(UnitTypeId.STARPORT).idle:
            return 1
    return 0


async def landAndReadyToBuildStarportAddOn_mask(self):
    if self.structures(UnitTypeId.STARPORTFLYING):
        if self.structures(UnitTypeId.STARPORTFLYING).idle:
            if self.can_afford(UnitTypeId.STARPORTREACTOR) and self.can_afford(UnitTypeId.STARPORTTECHLAB):
                for Starport in self.structures(UnitTypeId.STARPORTFLYING).idle:
                    possible_land_positions_offset = sorted(
                        (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                        key=lambda point: point.x ** 2 + point.y ** 2,
                    )
                    offset_point: Point2 = Point2((-0.5, -0.5))
                    possible_land_positions = (Starport.position.rounded + offset_point + p for p in possible_land_positions_offset)
                    for target_land_position in possible_land_positions:
                        land_and_addon_points: List[Point2] = land_positions(target_land_position)
                        if all(
                                self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos) and self.in_pathing_grid(land_pos)
                                for land_pos in land_and_addon_points
                        ):
                            Starport(AbilityId.LAND, target_land_position)
                            return 1
    return 0


async def expand_mask(self):
    if self.can_afford(UnitTypeId.COMMANDCENTER):
        return 1
    return 0


async def trainScv_mask(self):
    if self.can_afford(UnitTypeId.SCV):
        if self.supply_left >= 1:
            CCs: Units = self.townhalls()
            if CCs and len(self.units(UnitTypeId.SCV)) <= (22 * len(CCs)):
                for cc in CCs:
                    if cc.is_idle:
                        # cc.train(UnitTypeId.SCV)
                        return 1
    return 0


# 训练枪兵（至少一个）
async def trainMarine_mask(self):
    if self.structures(UnitTypeId.BARRACKS):
        if self.structures(UnitTypeId.BARRACKS).ready:
            if self.can_afford(UnitTypeId.MARINE):
                if self.supply_left >= 1:
                    return 1
    return 0


async def trainMarauder_mask(self):
    if self.structures(UnitTypeId.BARRACKS):
        barracks_ready = self.structures(UnitTypeId.BARRACKS).ready
        barracks_techlab_ready = barracks_ready.filter(lambda unit: unit.has_techlab == True)
        if barracks_techlab_ready:
            if self.can_afford(UnitTypeId.MARAUDER):
                if self.supply_left >= 2:
                    return 1
    return 0


async def trainGhost_mask(self):
    if self.structures(UnitTypeId.BARRACKS) and self.structures(UnitTypeId.GHOSTACADEMY):
        barracks_ready = self.structures(UnitTypeId.BARRACKS).ready
        barracks_techlab_ready = barracks_ready.filter(lambda unit: unit.has_techlab == True)
        if barracks_techlab_ready:
            if self.can_afford(UnitTypeId.MARAUDER):
                if self.supply_left >= 2:
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


async def trainViking_mask(self):
    if self.structures(UnitTypeId.STARPORT):
        starport_ready = self.structures(UnitTypeId.STARPORT).ready
        starport_techlab_ready = starport_ready.filter(lambda unit: unit.has_techlab == True)
        if starport_techlab_ready:
            if self.can_afford(UnitTypeId.VIKINGFIGHTER):
                if self.supply_left >= 2:
                    return 1
    return 0


async def trainThor_mask(self):
    if self.structures(UnitTypeId.FACTORY) and self.structures(UnitTypeId.ARMORY):
        factory_ready = self.structures(UnitTypeId.FACTORY).ready
        factory_techlab_ready = factory_ready.filter(lambda unit: unit.has_techlab == True)
        if factory_techlab_ready:
            if self.can_afford(UnitTypeId.THOR):
                if self.supply_left >= 2:
                    return 1
    return 0


async def trainRaven_mask(self):
    if self.structures(UnitTypeId.STARPORT):
        starport_ready = self.structures(UnitTypeId.STARPORT).ready
        starport_techlab_ready = starport_ready.filter(lambda unit: unit.has_techlab == True)
        if starport_techlab_ready:
            if self.can_afford(UnitTypeId.RAVEN):
                if self.supply_left >= 2:
                    return 1
    return 0


async def trainMedivac_mask(self):
    if self.structures(UnitTypeId.STARPORT):
        starport_ready = self.structures(UnitTypeId.STARPORT).ready
        starport_techlab_ready = starport_ready.filter(lambda unit: unit.has_techlab == True)
        if starport_techlab_ready:
            if self.can_afford(UnitTypeId.MEDIVAC):
                if self.supply_left >= 2:
                    return 1
    return 0


async def trainWidowmine_mask(self):
    if self.structures(UnitTypeId.FACTORY):
        if self.structures(UnitTypeId.FACTORY).ready:
            if self.can_afford(UnitTypeId.WIDOWMINE):
                if self.supply_left >= 2:
                    return 1
    return 0


async def trainBanshee_mask(self):
    if self.structures(UnitTypeId.STARPORT):
        starport_ready = self.structures(UnitTypeId.STARPORT).ready
        starport_techlab_ready = starport_ready.filter(lambda unit: unit.has_techlab == True)
        if starport_techlab_ready:
            if self.can_afford(UnitTypeId.BANSHEE):
                if self.supply_left >= 3:
                    return 1
    return 0


async def trainLiberator_mask(self):
    if self.structures(UnitTypeId.STARPORT):
        starport_ready = self.structures(UnitTypeId.LIBERATOR).ready
        starport_techlab_ready = starport_ready.filter(lambda unit: unit.has_techlab == True)
        if starport_techlab_ready:
            if self.can_afford(UnitTypeId.LIBERATOR):
                if self.supply_left >= 3:
                    return 1
    return 0


async def trainCyclone_mask(self):
    if self.structures(UnitTypeId.FACTORY):
        factory_ready = self.structures(UnitTypeId.FACTORY).ready
        factory_techlab_ready = factory_ready.filter(lambda unit: unit.has_techlab == True)
        if factory_techlab_ready:
            if self.can_afford(UnitTypeId.CYCLONE):
                if self.supply_left >= 3:
                    return 1
    return 0


async def trainSiegetank_mask(self):
    if self.structures(UnitTypeId.FACTORY):
        factory_ready = self.structures(UnitTypeId.FACTORY).ready
        factory_techlab_ready = factory_ready.filter(lambda unit: unit.has_techlab == True)
        if factory_techlab_ready:
            if self.can_afford(UnitTypeId.SIEGETANK):
                if self.supply_left >= 3:
                    return 1
    return 0


async def trainBattlecruiser_mask(self):
    if self.structures(UnitTypeId.STARPORT) and self.structures(UnitTypeId.FUSIONCORE):
        starport_ready = self.structures(UnitTypeId.STARPORT).ready
        starport_techlab_ready = starport_ready.filter(lambda unit: unit.has_techlab == True)
        if starport_techlab_ready:
            if self.can_afford(UnitTypeId.BATTLECRUISER):
                if self.supply_left >= 6:
                    return 1
    return 0


async def scvBackToWork_mask(self):
    if self.workers.idle:
        return 1
    return 0


async def detectionAndAttack_mask(self):
    if self.state.game_loop % ATTACK_FREQUENCY == 0:
        if self.mineral_field:
            if not self.enemy_structures:
                if not self.enemy_units:
                    if self.supply_army > 0:
                        return 1
    return 0


async def massNearEnemyBase_mask(self):
    if self.state.game_loop % ATTACK_FREQUENCY == 0:
        if self.enemy_structures:
            if self.supply_army > 10:
                return 1
    return 0


async def massNearBase_mask(self):
    if self.state.game_loop % ATTACK_FREQUENCY == 0:
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
                enemy_units = next((unit for unit in self.enemy_units), None)
                if self.structures.closest_distance_to(enemy_units) < 10:
                    return 1
    return 0


async def attackEnemySquad_mask(self):
    if self.state.game_loop % ATTACK_FREQUENCY == 0:
        if self.supply_army > 20:
            if self.enemy_units:
                return 1
    return 0


async def attackNearestBase_mask(self):
    if self.state.game_loop % ATTACK_FREQUENCY == 0:
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
        if economic_action[i] == buildBarracksTechlab:
            mask.append(await buildBarracksTechlab_mask(self))
        if economic_action[i] == buildBarracks:
            mask.append(await buildBarracks_mask(self))
        if economic_action[i] == liftBarracks:
            mask.append(await liftBarracks_mask(self))
        if economic_action[i] == landAndReadyToBuildBarracksAddOn:
            mask.append(await landAndReadyToBuildBarracksAddOn_mask(self))
        if economic_action[i] == buildEngineeringbay:
            mask.append(await buildEngineeringbay_mask(self))
        if economic_action[i] == buildRefinery:
            mask.append(await buildRefinery_mask(self))
        if economic_action[i] == buildFactoryReactor:
            mask.append(await buildFactoryReactor_mask(self))
        if economic_action[i] == buildFactoryTechlab:
            mask.append(await buildFactoryTechlab_mask(self))
        if economic_action[i] == buildFactory:
            mask.append(await buildFactory_mask(self))
        if economic_action[i] == liftFactory:
            mask.append(await liftFactory_mask(self))
        if economic_action[i] == landAndReadyToBuildFactoryAddOn:
            mask.append(await landAndReadyToBuildFactoryAddOn_mask(self))
        if economic_action[i] == buildGhostAcademy:
            mask.append(await buildGhostAcademy_mask(self))
        if economic_action[i] == buildMissileturret:
            mask.append(await buildMissileturret_mask(self))
        if economic_action[i] == buildSensortower:
            mask.append(await buildSensortower_mask(self))
        if economic_action[i] == buildBunker:
            mask.append(await buildBunker_mask(self))
        if economic_action[i] == buildArmory:
            mask.append(await buildArmory_mask(self))
        if economic_action[i] == buildFusioncore:
            mask.append(await buildFusioncore_mask(self))
        if economic_action[i] == buildStarport:
            mask.append(await buildStarport_mask(self))
        if economic_action[i] == buildStarportReactor:
            mask.append(await buildStarportReactor_mask(self))
        if economic_action[i] == buildStarportTechlab:
            mask.append(await buildStarportTechlab_mask(self))
        if economic_action[i] == liftStarport:
            mask.append(await liftStarport_mask(self))
        if economic_action[i] == landAndReadyToBuildStarportAddOn:
            mask.append(await landAndReadyToBuildStarportAddOn_mask(self))
        if economic_action[i] == expand:
            mask.append(await expand_mask(self))

        if economic_action[i] == trainScv:
            mask.append(await trainScv_mask(self))
        if economic_action[i] == trainMarine:
            mask.append(await trainMarine_mask(self))
        if economic_action[i] == trainHellion:
            mask.append(await trainHellion_mask(self))
        if economic_action[i] == trainMarauder:
            mask.append(await trainMarauder_mask(self))
        if economic_action[i] == trainGhost:
            mask.append(await trainGhost_mask(self))
        if economic_action[i] == trainViking:
            mask.append(await trainViking_mask(self))
        if economic_action[i] == trainBanshee:
            mask.append(await trainBanshee_mask(self))
        if economic_action[i] == trainThor:
            mask.append(await trainThor_mask(self))
        if economic_action[i] == trainRaven:
            mask.append(await trainRaven_mask(self))
        if economic_action[i] == trainMedivac:
            mask.append(await trainMedivac_mask(self))
        if economic_action[i] == trainWidowmine:
            mask.append(await trainWidowmine_mask(self))
        if economic_action[i] == trainCyclone:
            mask.append(await trainCyclone_mask(self))
        if economic_action[i] == trainSiegetank:
            mask.append(await trainSiegetank_mask(self))
        if economic_action[i] == trainBattlecruiser:
            mask.append(await trainBattlecruiser_mask(self))
        if economic_action[i] == trainLiberator:
            mask.append(await trainLiberator_mask(self))

        if economic_action[i] == scvBackToWork:
            mask.append(await scvBackToWork_mask(self))
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
