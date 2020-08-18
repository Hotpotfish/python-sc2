import sys, os
import tensorflow as tf
from examples.my_agent.my_agent_1.SqQueue import SqQueue
from examples.my_agent.my_agent_1.action_list import economic_action
from examples.my_agent.my_agent_1.get_state import get_state
from examples.my_agent.my_agent_1.net import net

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import random

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer


class RL_Bot(sc2.BotAI):
    def __init__(self):
        super().__init__()
        # self.
        self.memory = SqQueue(2e6)
        self.current_state = None
        self.action = None
        self.next_state = None
        self.reward = 0
        self.done = 0

        self.net = net(0, 1, 1e-3, len(economic_action), 62, 'net')
        self.session = tf.Session()
        self.session.run(tf.initialize_all_variables())

    async def on_step(self, iteration):
        # 62维
        current_state = get_state(self)

        if next_state is not None:
            pass

        index = random.sample(range(len(economic_action)), 1)[0]
        await economic_action[index](self)


def main():
    rlBot = RL_Bot()
    while 1:
        r = sc2.run_game(
            sc2.maps.get("Simple128"),
            [Bot(Race.Terran, rlBot, name="RL_bot"), Computer(Race.Protoss, Difficulty.VeryHard)],
            realtime=False,
        )
        # sc2.Result
        print(r)


if __name__ == "__main__":
    main()
