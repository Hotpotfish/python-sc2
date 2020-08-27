import numpy as np
import matplotlib.pyplot as plt

import seaborn as sns
import scipy.signal

bic_ddpg_data = []
central_v_data = []
coma_data = []
qmix_data = []
vdn_data = []

root = 'C:\\ProgramData\\Anaconda3\\Lib\\site-packages\\python-sc2\\examples\\my_agent\\rush_agent\\rush\\result\\'
al = ['bic_ddpg\\', 'central_v\\', 'coma\\', 'qmix\\', 'vdn\\']
map = 'Flat128'
ep = 'win_rate'
tail = '.npy'

for i in range(1):
    bic_ddpg_data.append(np.load(root + map + '\\' + ep + tail))
    # central_v_data.append(np.load(root + al[1] + map + '\\' + ep + str(i) + tail))
    # coma_data.append(np.load(root + al[2] + map + '\\' + ep + str(i) + tail)[0:200])
    # qmix_data.append(np.load(root + al[3] + map + '\\' + ep + str(i) + tail))
    # vdn_data.append(np.load(root + al[4] + map + '\\' + ep + str(i) + tail,allow_pickle=True))

# bic_ddpg_data = scipy.signal.savgol_filter(np.array(bic_ddpg_data), 21, 2, mode='nearest')
# central_v_data = scipy.signal.savgol_filter(np.array(central_v_data), 21, 2, mode='nearest')
# coma_data = scipy.signal.savgol_filter(np.array(coma_data), 21, 2, mode='nearest')
# qmix_data = scipy.signal.savgol_filter(np.array(qmix_data), 21, 2, mode='nearest')
# vdn_data = scipy.signal.savgol_filter(np.array(vdn_data), 21, 2, mode='nearest')

fig = plt.figure()
xdata = np.arange(0, len(bic_ddpg_data[0]))
linestyle = '-'
color = ['r', 'g', 'b', 'k', 'c']
label = ['rush', 'commnet', 'coma', 'qmix', 'vdn']

sns.tsplot(time=xdata, data=bic_ddpg_data, color=color[0], linestyle=linestyle, condition=label[0])
# sns.tsplot(time=xdata, data=central_v_data, color=color[1], linestyle=linestyle, condition=label[1])
# sns.tsplot(time=xdata, data=coma_data, color=color[2], linestyle=linestyle, condition=label[2])
# sns.tsplot(time=xdata, data=qmix_data, color=color[3], linestyle=linestyle, condition=label[3])
# sns.tsplot(time=xdata, data=vdn_data, color=color[4], linestyle=linestyle, condition=label[4])

plt.ylabel("win_rate", fontsize=15)
plt.xlabel("episode", fontsize=15)
plt.title(map, fontsize=20)
plt.show()
