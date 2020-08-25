from sc2 import UnitTypeId
import numpy as np

PL = 200


def get_state(self):
    return np.array([
        self.state.game_loop / 15000,
        self.minerals / 5000,
        self.vespene / 5000,
        self.supply_army / PL,
        self.supply_workers / PL,
        self.supply_cap / PL,
        self.supply_used / PL,
        self.supply_left / PL,
        self.idle_worker_count / PL,
        self.army_count / PL,

        len(self.townhalls) / 10,
        len(self.structures(UnitTypeId.SUPPLYDEPOT)) / 20,

        len(self.structures(UnitTypeId.BARRACKS)) / 10,
        len(self.structures(UnitTypeId.REFINERY)) / 10,
        len(self.structures(UnitTypeId.ENGINEERINGBAY)) / 10,

        len(self.units(UnitTypeId.MARINE)) / PL,
        len(self.units(UnitTypeId.MARAUDER)) / PL,

        len(self.enemy_units(UnitTypeId.MARINE)) / PL,
        len(self.enemy_units(UnitTypeId.MARAUDER)) / PL,
        len(self.enemy_units(UnitTypeId.REAPER)) / PL,
        len(self.enemy_units(UnitTypeId.GHOST)) / PL,
        len(self.enemy_units(UnitTypeId.HELLION)) / PL,
        len(self.enemy_units(UnitTypeId.SIEGETANK)) / PL,
        len(self.enemy_units(UnitTypeId.VIKING)) / PL,
        len(self.enemy_units(UnitTypeId.THOR)) / PL,
        len(self.enemy_units(UnitTypeId.MEDIVAC)) / PL,
        len(self.enemy_units(UnitTypeId.RAVEN)) / PL,
        len(self.enemy_units(UnitTypeId.BANSHEE)) / PL,
        len(self.enemy_units(UnitTypeId.WIDOWMINE)) / PL,
        len(self.enemy_units(UnitTypeId.LIBERATOR)) / PL,
        len(self.enemy_units(UnitTypeId.CYCLONE)) / PL,
        len(self.enemy_units(UnitTypeId.BATTLECRUISER)) / PL,

        len(self.enemy_structures(UnitTypeId.COMMANDCENTER)) / 10,
        len(self.enemy_structures(UnitTypeId.SUPPLYDEPOT)) / 20,
        len(self.enemy_structures(UnitTypeId.SUPPLYDEPOTLOWERED)) / 10,
        len(self.enemy_structures(UnitTypeId.BARRACKS)) / 10,
        len(self.enemy_structures(UnitTypeId.FACTORY)) / 10,
        len(self.enemy_structures(UnitTypeId.REFINERY)) / 10,
        len(self.enemy_structures(UnitTypeId.ENGINEERINGBAY)) / 10,
        len(self.enemy_structures(UnitTypeId.GHOSTACADEMY)) / 10,
        len(self.enemy_structures(UnitTypeId.MISSILETURRET)) / 10,
        len(self.enemy_structures(UnitTypeId.BUNKER)) / 10,
        len(self.enemy_structures(UnitTypeId.STARPORT)) / 10,
        len(self.enemy_structures(UnitTypeId.ARMORY)) / 10,
        len(self.enemy_structures(UnitTypeId.FUSIONCORE)) / 10,
    ])
