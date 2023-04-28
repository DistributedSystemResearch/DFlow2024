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

plt.figure(figsize=(9, 4))

excelblue = '#4472C4'    # (68, 114, 196)
excelorange = '#ED7D31'  # (237, 125, 49)

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
blue, orange, green, red = colors[:4]


x = np.arange(7)

bar_width = 0.26
tick_label = ["0.1","0.4","1","10","20","50","100"]
#tick_label = ["10KB","100KB","1MB","10MB"]

df1 = pd.read_csv('DStoreGet1.csv')
df2 = pd.read_csv('CouchDBGet.csv')

y_1 = list(df1['time'][2:]) # DStore get
y_2 = list(df2['time'][2:]) # CouchDB get

print(y_1)
print(y_2)
inds = np.arange(len(y_1))
for i in range(len(y_1)):
    y_1[i] = y_1[i] * 1000
    y_2[i] = y_2[i] * 1000
print(y_1)
print(y_2)

nbars = 4
width = 0.8 / nbars
line_config = dict(edgecolor='white')

plt.bar(inds-(width/2+width), np.array(y_2), width, color=orange, **line_config)
#[21:39] Xiaoxiang Shi (FA Talent)
plt.text(0 -(width/2 + width)-0.2, 10,'7.5', dict(font='DejaVu Sans', size=20, color=orange))

#plt.text(1 -(width/2 + width), 10, 'X', dict(font='DejaVu Sans', size=18, color=orange))


# Alpa
plt.bar(inds-(width/2), np.array(y_1), width, color=blue, **line_config)
plt.text(0 -(width/2), 10,'2.1', dict(font='DejaVu Sans', size=20, color=blue))
my_labels = ["CouchDB", "DStore"]
plt.legend(fontsize=24, ncol=1, frameon=False, labels = my_labels) # loc='lower right', #bbox_to_anchor=(0.9, 0.90)

plt.xlabel("Data Size(MB)", dict(size=22))
plt.xticks(inds, tick_label[2:], fontsize=20)

plt.ylabel('Latency(ms)', dict(size=24))

plt.yticks(np.array([10,200,400,600]), fontsize=24)
plt.grid(axis="y", linewidth =0.15, linestyle = '--')
plt.tight_layout()
plt.show()

# # # y_1 = y_1[:4]
# # # y_2 = y_2[:4]
# # # print(len(y_1))
# # #ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
# # #ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#74a9cf", align="center", label="CouchDB",edgecolor='black',linewidth=1)
# # #ax1.bar(x+0.5*bar_width, y_1, bar_width, color="#9bbb59", align="center", label="DStore",edgecolor='black',linewidth=1)
# # ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#74a9cf", align="center",edgecolor='black',linewidth=1)
# # ax1.bar(x+0.5*bar_width, y_1, bar_width, color="#9bbb59", align="center",edgecolor='black',linewidth=1)
# # #ax1.bar(x+1.5*bar_width, y_4, bar_width, color="#FFFED5", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)
# # #F7903D#59A95A#4D85BD

# #ax1.set_ylim(0,100)
# ax1.tick_params(labelsize=32)
# ax1.set_xticklabels(tick_label, fontsize=30)
# ax1.set_ylabel('The get latency(ms)', fontsize=30)
# # plt.yticks([0, 1, 2,3,4], ["0.1","1" , "10", "100","1000"],fontsize=32)
# #ax1.set_title("Get latencies",fontsize=30)
# plt.xticks(x, tick_label,rotation=0)
# plt.yticks(fontsize = 20)
# # ls =  [0, 40,  500] # yticks([0, 20, 40, 60, 80, 100, 500])
# # ls = np.array(ls)
# # plt.yticks(ls)
# """
# ax1.axhline(y=20, color='tab:grey', linestyle='--')
# ax1.axhline(y=40, color='tab:grey', linestyle='--')
# ax1.axhline(y=60, color='tab:grey', linestyle='--')
# ax1.axhline(y=80, color='tab:grey', linestyle='--')
# """
# #ax1.plot(label = 'CouchDB')
# #ax1.plot(label = 'DStroe')
# ax1.legend(ncol=1,loc='upper left',fontsize=20, labels = ['CouchDB','DStore'])
# #ax1.legend(ncol=2,loc='upper left',fontsize=20)

# # 设置子图之间的间距，默认值为1.08
# plt.tight_layout(pad=0.12)  
plt.savefig("e2e-get-latency.pdf", bbox_inches='tight')
plt.show()