from sc2 import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units


def validity_check(self):
    pass


async def buildSupplydepot_check(self):
    # Can return None if no position was found
    if self.can_afford(UnitTypeId.SUPPLYDEPOT):
        if self.works:
            CCs: Units = self.townhalls()
            cc: Unit = CCs.first
            placement_position = await self.find_placement(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8))
            if placement_position:
                return 1
    return 0


async def buildBarracks_check(self):
    # Can return None if no position was found
    if self.structures(UnitTypeId.SUPPLYDEPOT) or self.structures(UnitTypeId.SUPPLYDEPOTLOWERED):
        if self.can_afford(UnitTypeId.BARRACKS):
            if self.works:
                CCs: Units = self.townhalls()
                cc: Unit = CCs.first
                placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 8))
                if placement_position:
                    return 1
    return 0

async def buildRefinery_check(self):
    # Can return None if no position was found
    if self.can_afford(UnitTypeId.REFINERY):
        # All the vespene geysirs nearby, including ones with a refinery on top of it
        CCs: Units = self.townhalls()
        cc: Unit = CCs.first
        vgs = self.vespene_geyser.closer_than(10, cc)
        for vg in vgs:
            if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
                continue
    return 0

# if self.can_afford(UnitTypeId.SUPPLYDEPOT):
#     return 1
# else:
#     return 0
