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

fig = plt.figure(figsize=(19, 7))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
ax1 = fig.add_subplot(gs[0])   # 2*1
# 第一个图为

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

# fig = plt.figure(figsize=(9, 4))

# plt.rcParams["font.family"] = "Times New Roman"

plt.figure(figsize=(9,4)) #12 * 7 

# excelblue = '#4472C4'    # (68, 114, 196)
# excelorange = '#ED7D31'  # (237, 125, 49)

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
blue, orange, green, red = colors[:4]

plt.rcParams.update({'font.size': 28})
x = np.arange(6)

bar_width = 0.15
# 3tick_label = ["Epi","Gen","Soy","FP","WC","helloworld"]
tick_label = ["Cyc","Epi","Gen","Soy","FP","WC"]
# tick_label = ["10KB","100KB","1MB","10MB"]
inds = np.arange(len(tick_label))
cflow_single = list(pd.read_csv("raw_single.csv")["e2e_latency"])
cflow_corun = list(pd.read_csv("raw_corun.csv")["e2e_latency"])

faasflow_single = list(pd.read_csv("optimized_single.csv")["e2e_latency"])
faasflow_corun = list(pd.read_csv("optimized_corun.csv")["e2e_latency"])

dflow_single = list(pd.read_csv("optimized_single_DFlow.csv")["e2e_latency"])
dflow_corun = list(pd.read_csv("optimized_corun_DFlow.csv")["e2e_latency"])
# ideal = list(pd.read_csv("ideal.csv")["e2e_latency"])[:4]
ideal_corun = list(pd.read_csv("ideal.csv")["e2e_latency"])

def convert(data):
    for i in range(len(data)):
        if data[i] == 'timeout':
            data[i] = 60
        else:
            data[i] = float(data[i])
    data = np.array(data)
    return data 

cflow_single = convert(cflow_single)
cflow_corun = convert(cflow_corun)

faasflow_single = convert(faasflow_single)

faasflow_corun = convert(faasflow_corun)

dflow_single = convert(dflow_single)
dflow_corun = convert(dflow_corun)

def calculate_degrade(single, corun):
    result = [] 
    for i in range(len(tick_label)):
        result.append((corun[i] / single[i])) 
    return np.array(result)
#print(faasflow_single, faasflow_corun)
cflow_degrade =  calculate_degrade(cflow_single,cflow_corun)
faasflow_degrade = calculate_degrade(faasflow_single, faasflow_corun)
dflow_degrade = calculate_degrade(dflow_single, dflow_corun)

print(cflow_degrade)
print(faasflow_degrade)
print(dflow_degrade)
ideal_degrade = np.ones(len(dflow_degrade))
#ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
#ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#C46025", align="center", label="HyperFlow-serverless co-run",edgecolor='black',linewidth=2)
#ax1.bar(x+0.5*bar_width, y_3, bar_width, color="#F0AC48", align="center", label="FaaSFlow-FaaStore solo-run",edgecolor='black',linewidth=2)
#ax1.bar(x+1.5*bar_width, y_4, bar_width, color="#FFFED5", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)

#ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
ax1.bar(x-0.5*bar_width,cflow_corun, bar_width, color=orange, align="center", label="CFlow co-run",edgecolor='black',linewidth=2)
#ax1.bar(x+0.5*bar_width, y_3, bar_width, color="#F0AC48", align="center", label="FaaSFlow-FaaStore solo-run",edgecolor='black',linewidth=2)
ax1.bar(x+0.5*bar_width, faasflow_corun, bar_width, color=green, align="center", label="FaaSFlow co-run",edgecolor='black',linewidth=2)
ax1.bar(x+1.5*bar_width, dflow_corun, bar_width, color=blue, align="center", label="DFlow co-run",edgecolor='black',linewidth=2)
#F7903D#59A95A#4D85BD
ax1.bar(x+2.5*bar_width, ideal_corun, bar_width, color="lightgrey", align="center", label="Ideal co-run",edgecolor='black',linewidth=2)
#ax1.set_xticklabels(tick_label, fontsize=28)
ax1.set_ylim(0,60)
ax1.tick_params(labelsize=30)
# tick_label = ["Cyc","Epi","Gen","Soy","FP","WC"]
# ax1.xticks(tick_label, fontsize=20)
ax1.set_xticks(np.arange(6))
ax1.set_xticklabels(tick_label, fontsize=28)
ax1.set_ylabel('The End-to-end Latencies\n Interference when co-running', fontsize=28)


plt.xticks(x, tick_label,rotation=0)
#plt.xticks(x, tick_label,rotation=0)
# ax1.axhline(y=4, color='tab:lightgrey', linestyle='--')
# ax1.axhline(y=8, color='tab:lightgrey', linestyle='--')
# ax1.axhline(y=12, color='tab:lightgrey', linestyle='--')
# ax1.axhline(y=16, color='tab:lightgrey', linestyle='--')
# ax1.axhline(y=20, color='tab:lightgrey', linestyle='--')
# ax1.axhline(y=24, color='tab:lightgrey', linestyle='--')
# ax1.axhline(y=28, color='tab:lightgrey', linestyle='--')
ax1.legend(ncol=1,loc='upper left',fontsize=24,handlelength=1.7)



ax2 = ax1.twinx()
ax2.plot(x, cflow_degrade, color=orange,linewidth=3,label='CFlow degradation',marker='o', ms=12)
ax2.plot(x,faasflow_degrade, color=green,linewidth=3,label='FaaSFlow degradation',marker='o', ms=12)
ax2.plot(x,dflow_degrade, color=blue,linewidth=3,label='DFlow degradation',marker='o', ms=12)
ax2.plot(x,ideal_degrade, color="lightgrey",linewidth=3,label='Ideal degradation',marker='o', ms=12)
ax2.set_ylim(0,4)
ax2.legend(ncol=1,loc='upper right',fontsize=24,handlelength=1.7)
ax2.set_ylabel('The end-to-end degradation\n normalized to solo-run', fontsize=28)
# ax2.set_xticklabels(tick_label, fontsize=28)

# y2_major_locator=MultipleLocator(0.5)
# #把y轴的刻度间隔设置为10，并存在变量里
# ax2.yaxis.set_major_locator(y2_major_locator)

# y1_major_locator=MultipleLocator(4)
# #把y轴的刻度间隔设置为10，并存在变量里
# ax1.yaxis.set_major_locator(y1_major_locator)


# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
fig.savefig("co-location-ideal.pdf", bbox_inches='tight')
plt.show()
