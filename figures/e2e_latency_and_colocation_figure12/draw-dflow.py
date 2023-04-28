# sudo apt-get install texlive-extra-utils
# pdfcrop input.pdf output.pdf
# bash
# for FILE in ./*.pdf; do
#   pdfcrop "${FILE}"
# done

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
x = np.arange(4)

bar_width = 0.15
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
    for i in range(len(single)):
        result.append(corun[i] / single[i])
    return np.array(result)

cflow_degrade =  calculate_degrade(cflow_single,cflow_corun)
faasflow_degrade = calculate_degrade(faasflow_single, faasflow_corun)
dflow_degrade = calculate_degrade(dflow_single, dflow_corun)

nbars = 4
width = 0.8 / nbars
line_config = dict(edgecolor='white')

plt.bar(inds-(width/2+width), cflow_corun, width,hatch='x', color=orange, **line_config)

plt.bar(inds-(width/2), faasflow_corun, width,hatch='-', color=green, **line_config)


plt.bar(inds+(width/2), dflow_corun, width, color=blue, **line_config)

plt.ylabel('The 99%-ile-latency(s)', dict(size=20))
plt.grid(axis="y", linewidth =0.3, linestyle = '--')
plt.yticks(np.array([0, 4, 8, 12, 16,20, 24,28]), fontsize=22)

# size = np.arange(6)
# line1 = plt.plot(size, cflow_degrade, linestyle='dashed', marker='o', markersize=10, color=orange, **line_config)
# line1 = plt.plot(size, faasflow_degrade, linestyle='dashed', marker='o', markersize=10, color=orange, **line_config)
# line1 = plt.plot(size, faasflow_degrade, linestyle='dashed', marker='o', markersize=10, color=orange, **line_config)
# line1 = plt.plot(size, cflow, linestyle='dashed', marker='o', markersize=10, color=orange, **line_config)\


# line2 = plt.plot(size, faasflow, linestyle='dashdot', marker='s', markersize=10, color=green, **line_config)


# line3 = plt.plot(size, dflow, linestyle='solid', marker='s', markersize=10, color=blue, **line_config)

# line4 = plt.plot(size, ideal, linestyle='dotted', marker='s', markersize=10, color=red, **line_config)

# ax1.axhline(y=4, color='tab:grey', linestyle='--')
# ax1.axhline(y=8, color='tab:grey', linestyle='--')
# ax1.axhline(y=12, color='tab:grey', linestyle='--')
# ax1.axhline(y=16, color='tab:grey', linestyle='--')
# ax1.axhline(y=20, color='tab:grey', linestyle='--')
# ax1.axhline(y=24, color='tab:grey', linestyle='--')
# ax1.axhline(y=28, color='tab:grey', linestyle='--')

# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
plt.savefig("co-location.pdf", bbox_inches='tight')
plt.show()