import sys, os
import tensorflow as tf
from examples.my_agent.my_agent_1.SqQueue import SqQueue
from examples.my_agent.my_agent_1.action_list import economic_action
from examples.my_agent.my_agent_1.get_reward import get_reward
from examples.my_agent.my_agent_1.get_state import get_state
from examples.my_agent.my_agent_1.net import net
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import random

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

EPSIODES = 2000
BATCH_SIZE = 32
GAMMA = 0.99


class RL_Bot(sc2.BotAI):
    def __init__(self):
        super().__init__()
        # self.
        self.memory = SqQueue(2e6)
        self.current_state = None
        self.action = None
        self.next_state = None
        # self.reward = 0
        # self.done = None

        self.action_dim = len(economic_action)

        self.init_epsilon = 0.5
        self.fin_epsilon = 0.01
        self.current_epsilon = self.init_epsilon

        self.net = net(0, 1, 1e-3, self.action_dim, 62, 'net')
        self.session = tf.Session()
        self.session.run(tf.initialize_all_variables())

    async def on_step(self, iteration):
        # print(iteration)
        # 62维
        self.current_state = get_state(self)
        q = self.session.run(self.net.q, {self.net.state: self.current_state[np.newaxis]})[0]

        if random.random() <= self.current_epsilon:
            self.action = random.randint(0, self.action_dim - 1)
        else:
            self.action = np.argmax(q)
        self.current_epsilon = - (self.init_epsilon - self.fin_epsilon) / (EPSIODES * 2000)
        # print(self.action)
        if self.next_state is not None:
            self.memory.inQueue([self.current_state, np.eye(self.action_dim)[self.action], 0, self.next_state, 0])
        await economic_action[self.action](self)
        self.next_state = self.current_state

        if self.memory.real_size > BATCH_SIZE:
            minibatch = random.sample(self.memory.queue, BATCH_SIZE)
            state = np.array([data[0] for data in minibatch])
            action_batch = np.array([data[1] for data in minibatch])
            reward_batch = np.array([data[2] for data in minibatch])
            state_next = np.array([data[3] for data in minibatch])
            terminateds = np.array([data[4] for data in minibatch])

            q_ = np.max(self.session.run(self.net.q_, {self.net.state_next: state_next}), axis=1)[:,np.newaxis]
            y_input = np.squeeze(reward_batch[:, np.newaxis] + GAMMA * q_ * (np.array(abs(terminateds - 1))[:, np.newaxis]))
            self.session.run([self.net.trian_op, self.net.loss], {self.net.y_input: y_input,
                                                                  self.net.state: state,
                                                                  self.net.action_input: action_batch})


def main():
    rlBot = RL_Bot()
    n_epsiodes = EPSIODES
    while n_epsiodes != 0:
        r = sc2.run_game(
            sc2.maps.get("Simple128"),
            [Bot(Race.Terran, rlBot, name="RL_bot"), Computer(Race.Protoss, Difficulty.VeryHard)],
            realtime=False,
        )
        # sc2.Result
        reward = get_reward(r)
        rlBot.memory.deleteLastOne()
        rlBot.memory.inQueue([rlBot.current_state, np.eye(rlBot.action_dim)[rlBot.action], reward, rlBot.next_state, 1])
        rlBot.current_state = None
        rlBot.action = None
        # rlBot.current_state
        rlBot.next_state = None

        n_epsiodes -= 1


if __name__ == "__main__":
    main()
