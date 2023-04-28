import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib as mpl
import matplotlib.ticker as mtick  
#from brokenaxes import brokenaxes
from matplotlib import gridspec
from matplotlib.pyplot import MultipleLocator

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib as mpl
import matplotlib.ticker as mtick  
#from brokenaxes import brokenaxes
from matplotlib import gridspec
from matplotlib.pyplot import MultipleLocator


# plt.rcParams["font.family"] = "Times New Roman"



excelblue = '#4472C4'    # (68, 114, 196)
excelorange = '#ED7D31'  # (237, 125, 49)

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
blue, orange, green, red = colors[:4]

fig = plt.figure(figsize=(9, 4))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
# ax1 = fig.add_subplot(gs[0])   # 2*1
# 第一个图为
plt.rcParams.update({'font.size': 28})
x = np.arange(4)

bar_width = 0.15
tick_label = ["Cyc","Epi","Gen","Soy"]
# tick_label = ["10KB","100KB","1MB","10MB"]
inds = np.arange(4)
cflow = list(pd.read_csv("raw_6rpm_50MB_2023_plus_DStore.csv")["tail_latency"])
faasflow = list(pd.read_csv("optimized_6rpm_50MB_2023_plus_DStore.csv")["tail_latency"])
dflow = list(pd.read_csv("DFlow-optimized-6rpm-50MB.csv")["tail_latency"][:4])
# ideal = list(pd.read_csv("ideal-6rpm-50MB.csv")["tail_latency"])

def convert(data):
    for i in range(len(data)):
        if data[i] == 'timeout':
            data[i] = 60
        else:
            data[i] = float(data[i])
    return data 

cflow = convert(cflow)

faasflow = convert(faasflow)

dflow = convert(dflow)
# ideal = convert(ideal)





nbars = 4
width = 0.8 / nbars
line_config = dict(edgecolor='white')

plt.bar(inds-(width/2+width), np.array(cflow), width,hatch='x', color=orange, **line_config)

plt.bar(inds-(width/2), np.array(faasflow), width,hatch='-', color=green, **line_config)


plt.bar(inds+(width/2), np.array(dflow), width, color=blue, **line_config)

# plt.bar(inds+(width/2+width), np.array(ideal), width,  color="lightgrey", **line_config)

my_labels = ["CFlow", "FaaSFlow", "DFlow"]
plt.legend(fontsize=20, ncol=1, frameon=False, labels = my_labels) # loc='lower right', #bbox_to_anchor=(0.9, 0.90)

# plt.xlabel("Data Size(MB)", dict(size=22))
plt.xticks(inds, tick_label, fontsize=20)

plt.ylabel('The 99%-ilatency(s)', dict(size=20))

# plt.yticks(np.array([200,600,1000]), fontsize=22)
plt.grid(axis="y", linewidth =0.15, linestyle = '--')
plt.yticks(np.array([0,10,20,30,40,50,60]), fontsize=20)
plt.savefig("invocation-patteron-study.pdf", bbox_inches='tight')

plt.show()
plt.tight_layout()
plt.show()

