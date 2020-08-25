import sys, os
import tensorflow as tf
from examples.my_agent.rush_agent.SqQueue import SqQueue
from examples.my_agent.rush_agent.action_list import economic_action
from examples.my_agent.rush_agent.get_reward import get_reward
from examples.my_agent.rush_agent.get_state import get_state
from examples.my_agent.rush_agent.macro_action_mask import getMask
from examples.my_agent.rush_agent.net import net
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import random

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer, Human

EPSIODES = 2000
BATCH_SIZE = 512
GAMMA = 0.99
SAVE_CYCLE = 10
HARD_REPLACE = 2000


class RL_Bot(sc2.BotAI):
    def __init__(self, map_name):
        super().__init__()
        # self.
        self.memory = SqQueue(2e6)
        self.current_state = None
        self.action = None
        self.next_state = None
        # self.reward = 0
        # self.done = None
        self.win = 0

        self.test_tag = False

        self.action_dim = len(economic_action)

        self.init_epsilon = 1
        self.fin_epsilon = 0.01
        self.current_epsilon = self.init_epsilon

        self.net = net(0, 1, 1e-3, self.action_dim, 45, 'net')

        self.session = tf.Session()
        self.writer = tf.summary.FileWriter("rush/logs/" + map_name, self.session.graph)
        self.step = 0
        self.saver = tf.train.Saver()
        self.session.run(tf.initialize_all_variables())

        self.research_combatshield = 0
        self.eConcussiveshells = 0

    async def on_step(self, iteration):
        # print(iteration)
        # 62维
        self.current_state = get_state(self)
        q = np.array(self.session.run(self.net.q, {self.net.state: self.current_state[np.newaxis]})[0])
        mask = await getMask(self)

        q = q * mask
        if not self.test_tag:

            if random.random() <= self.current_epsilon:
                self.action = np.random.choice(np.nonzero(np.array(mask))[0])
            else:
                self.action = np.argmax(q)
        else:
            self.action = np.argmax(q)
        self.current_epsilon -= (self.init_epsilon - self.fin_epsilon) / (EPSIODES * 2000)
        # print(self.action)
        if self.next_state is not None:
            self.memory.inQueue([self.current_state, np.eye(self.action_dim)[self.action], 0, self.next_state, 0])
        await economic_action[self.action](self)
        self.next_state = self.current_state

        if self.memory.real_size > BATCH_SIZE * 6 and not self.test_tag:
            minibatch = random.sample(self.memory.queue, BATCH_SIZE)
            state = np.array([data[0] for data in minibatch])
            action_batch = np.array([data[1] for data in minibatch])
            reward_batch = np.array([data[2] for data in minibatch])
            state_next = np.array([data[3] for data in minibatch])
            terminateds = np.array([data[4] for data in minibatch])

            q_ = np.max(self.session.run(self.net.q_, {self.net.state_next: state_next}), axis=1)[:, np.newaxis]
            y_input = np.squeeze(reward_batch[:, np.newaxis] + GAMMA * q_ * (np.array(abs(terminateds - 1))[:, np.newaxis]))
            _, merged_summary = self.session.run([self.net.trian_op, self.net.merged_summary], {self.net.y_input: y_input,
                                                                                                self.net.state: state,
                                                                                                self.net.action_input: action_batch})
            self.writer.add_summary(merged_summary, self.step)
            self.step += 1
            if iteration % HARD_REPLACE == 0:
                self.session.run(self.net.hard_replace)


def main():
    map_name = "Flat128"
    rlBot = RL_Bot(map_name)

    # rlBot.map_name = map_name
    if not rlBot.test_tag:
        n_epsiodes = EPSIODES
        win_rate = []
        while n_epsiodes >= 0:
            # 保存模型
            if n_epsiodes % SAVE_CYCLE == 0:
                isExists = os.path.exists("rush/model/" + map_name)
                if not isExists:
                    os.makedirs("rush/model/" + map_name)
                rlBot.saver.save(rlBot.session, "rush/model/" + map_name + "/save.ckpt")

            r = sc2.run_game(
                sc2.maps.get(map_name),
                [Bot(Race.Terran, rlBot, name="RL_bot"), Computer(Race.Terran, Difficulty.Hard)],
                realtime=False,
            )
            reward = get_reward(r)

            rlBot.memory.inQueue([rlBot.current_state, np.eye(rlBot.action_dim)[rlBot.action], reward, rlBot.next_state, 1])
            rlBot.current_state = None
            rlBot.action = None
            rlBot.next_state = None
            rlBot.research_combatshield = 0
            rlBot.eConcussiveshells = 0
            n_epsiodes -= 1
            if reward == 1:
                rlBot.win += 1
            win_rate.append(rlBot.win / (EPSIODES - n_epsiodes))
            isExists = os.path.exists("rush/result/" + map_name)
            if not isExists:
                os.makedirs("rush/result/" + map_name)
            np.save("rush/result/" + map_name + '/win_rate', win_rate)
            print("epsiodes: %d  win_rate: %f" % (EPSIODES - n_epsiodes, rlBot.win / (EPSIODES - n_epsiodes)))
    else:
        rlBot.saver.restore(rlBot.session, "rush/model/" + map_name + "/save.ckpt")
        sc2.run_game(
            sc2.maps.get("Flat128"),
            [Human(Race.Terran, fullscreen=True), Bot(Race.Terran, rlBot, name="RL_bot")],
            realtime=True,
        )


if __name__ == "__main__":
    main()
