import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np


class net(object):

    def __init__(self, mu, sigma, learning_rate, action_dim, state_dim, name):  # 初始化
        # 神经网络参数
        self.mu = mu
        self.sigma = sigma
        self.learning_rate = learning_rate

        # 动作维度数，动作参数维度数,状态维度数
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.name = name

        self._setup_placeholders_graph()

        self.q = self._build_graph_q(self.state, 'q', True)
        self.q_ = self._build_graph_q(self.state_next, 'q_', False)
        self.qe_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='q')
        self.qt_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='q_')

        self.trian_op, self.loss = self.create_training_method(self.action_input, self.q, self.y_input)

        self.hard_replace = [tf.assign(t, e) for t, e in zip(self.qt_params, self.qe_params)]
        self.merged_summary = tf.summary.merge_all()

    def _setup_placeholders_graph(self):
        # s
        self.state = tf.placeholder("float", shape=[None, self.state_dim], name='state')
        self.state_next = tf.placeholder("float", shape=[None, self.state_dim], name='state_next')
        self.y_input = tf.placeholder("float", shape=[None], name='y_input')
        self.action_input = tf.placeholder("float", [None, self.action_dim], name='action_input')

    def _build_graph_q(self, state_input, scope_name, train):
        # 环境和智能体本地的共同观察
        with tf.variable_scope(scope_name, reuse=tf.AUTO_REUSE):
            with slim.arg_scope([slim.conv2d, slim.fully_connected],
                                trainable=train,
                                activation_fn=tf.nn.relu,
                                normalizer_fn=slim.batch_norm,
                                weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                weights_regularizer=slim.l2_regularizer(0.05)):
                fc1 = slim.fully_connected(state_input, 50, scope='fc1')
                fc2 = slim.fully_connected(fc1, 30, scope='fc2')
                action = slim.fully_connected(fc2, self.action_dim, activation_fn=tf.nn.softmax, scope='action_output')
                return action

    def create_training_method(self, action_input, q_value, y_input):
        Q_action = tf.reduce_sum(tf.multiply(q_value, action_input), axis=1)
        cost = tf.reduce_mean(tf.square(y_input - Q_action))
        train_op = tf.train.AdamOptimizer(self.learning_rate).minimize(cost)
        tf.summary.scalar("loss", cost)
        return train_op, cost
