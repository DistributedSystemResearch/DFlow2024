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

plt.figure(figsize=(12,7)) #12 * 7 

# excelblue = '#4472C4'    # (68, 114, 196)
# excelorange = '#ED7D31'  # (237, 125, 49)

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
blue, orange, green, red = colors[:4]

plt.rcParams.update({'font.size': 28})
x = np.arange(4)

bar_width = 0.15
tick_label = ["2","4","6","8", "10"]
# tick_label = ["10KB","100KB","1MB","10MB"]
inds = np.arange(len(tick_label))
cflow = list(pd.read_csv("raw_genome_75MB-2023-cflow.csv")["tail_latency"])
faasflow = list(pd.read_csv("optimized_genome_75MB.csv")["tail_latency"])
dflow = list(pd.read_csv("optimized_genome_75MB_DFlow.csv")["tail_latency"])
ideal = list(pd.read_csv("ideal.csv")["tail_latency"])

def convert(data):
    for i in range(len(data)):
        if data[i] == 'timeout':
            data[i] = 60
        else:
            data[i] = float(data[i])
    data = np.array(data)
    return data 

cflow = convert(cflow)

faasflow = convert(faasflow)

dflow = convert(dflow)
ideal = convert(ideal)
size = [2, 4, 6, 8, 10]

labels = ["CFlow","FaaSFlow","DFlow","Ideal"]

line_config = dict(linewidth=2)






nbars = 4
width = 0.8 / nbars
line_config = dict(edgecolor='white')

# plt.bar(inds-(width/2+width), np.array(cflow), width,hatch='x', color=orange, **line_config)

# plt.bar(inds-(width/2), np.array(faasflow), width,hatch='-', color=green, **line_config)


# plt.bar(inds+(width/2), np.array(dflow), width, color=blue, **line_config)

# plt.bar(inds+(width/2+width), np.array(ideal), width,  color="lightgrey", **line_config)


plt.bar(inds-(width/2+width), np.array(cflow), width, color=orange, **line_config)

plt.bar(inds-(width/2), np.array(faasflow), width, color=green, **line_config)


plt.bar(inds+(width/2), np.array(dflow), width, color=blue, **line_config)

plt.bar(inds+(width/2+width), np.array(ideal), width,  color="lightgrey", **line_config)
# line1 = plt.plot(size, cflow, linestyle='dashed', marker='o', markersize=10, color=orange, **line_config)\


# line2 = plt.plot(size, faasflow, linestyle='dashdot', marker='s', markersize=10, color=green, **line_config)


# line3 = plt.plot(size, dflow, linestyle='solid', marker='s', markersize=10, color=blue, **line_config)

# line4 = plt.plot(size, ideal, linestyle='dotted', marker='s', markersize=10, color=red, **line_config)


plt.legend(fontsize=18, loc = "upper left", ncol=1,labels = labels, frameon=False) # loc='lower right', #bbox_to_anchor=(0.9, 0.90)
plt.xticks(inds, tick_label, fontsize=20)
# plt.xlabel('GPU Number', dict(size=22))
# my_ticks = np.array([0, 5, 15, 25, 40,55,60])
# plt.xticks(my_ticks, fontsize=24)
plt.xlabel('Throughput(req/min)', dict(size=20))
plt.ylabel('The 99%-ile-latency(s)', dict(size=20))
plt.grid(axis="y", linewidth =0.3, linestyle = '--')
plt.yticks(np.array([5, 15, 25, 60]), fontsize=22)

plt.title('(c)Gen-75MB/s', fontsize =25)

plt.tight_layout()
# plt.show()
plt.savefig('gen-75MB.pdf')
plt.show()
plt.tight_layout()
