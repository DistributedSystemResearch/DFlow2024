import sys
from typing import Dict, List
import test_parse_yaml
import queue
import json
import component
import repository
import config
import time
import yaml
import uuid

mem_usage = 0
max_mem_usage = 0
group_ip = {}
group_scale = {}

def init_graph(workflow, group_set, node_info):
    global group_ip, group_scale
    ip_list = list(node_info.keys()) #ip值
    print("****ip_list****",ip_list)
    in_degree_vec = dict()
    q = queue.Queue()
    #workflow.start_functions表示的是这个workflow(DAG)入度为0的函数
    #! 对于wordcount来说,workflow.start_functions = ["start"]
    for name in workflow.start_functions:
        q.put(workflow.nodes[name])#加入队列
        group_set.append((name, ))###加入group_set,这个group set是可以变的吗，因为它是参数
        #! group_set变化了吗
    while q.empty() is False:
        node = q.get() #? node是DAG重入度为0的点
        for next_node_name in node.next:
            #? node.next表示这个节点的后续节点，可能有多个
            #! in_degree_vec存这个next_node_name有多个入度节点
            #!比如说A->B,C->B,A和C是入度为0的点，B的入度为2 
            if next_node_name not in in_degree_vec:
                in_degree_vec[next_node_name] = 1 
                q.put(workflow.nodes[next_node_name]) #todo:这一步将workflow.nodes[next_node_name]加入了q是为啥呢
                #!  workflow.nodes记录了整个函数的工作流，workflow.nodes[next_node_name]是某个·DAG中的一个点
                group_set.append((next_node_name, )) #todo:这里不是很理解，为什么要把next_node_name也加入group_set
                #12-10,没有相同为什么把next_node_name加入group_set
            else:
                in_degree_vec[next_node_name] += 1
    for s in group_set:
        #s是一个函数名，group_ip[s]是一个ip
        ###s是('start',)
        print('*********s:',s,'**********\n')
        print('*********s[0]:',s[0],'**********\n')
        group_ip[s] = ip_list[hash(s) % len(ip_list)] #把某个入度为0的函数给与一个ip吗，让其执行，即这个函数被分配到了某台机器
        ##todo(lambda):这里不一定负载均衡
        group_scale[s] = workflow.nodes[s[0]].scale
        #todo:s[0]是什么,s[0]是start, count 
        node_info[group_ip[s]] -= workflow.nodes[s[0]].scale
        ###这里用s[0]是什么意思
        ###node_info的key为ip,value表示容器数量，47行执行完后，表示这个节点用掉了workflow.nodes[s[0]].scale个容器
        ###所以要减去
    return in_degree_vec


def find_set(node, group_set):
    ##todo:这里得理解下
    for node_set in group_set:
        print("\n*****node_set",node_set,'********\n')
        if node in node_set:
            return node_set
    return None


def topo_search(workflow: component.workflow, in_degree_vec, group_set):
    dist_vec = dict()  # { name: [dist, max_length] }
    prev_vec = dict()  # { name: [prev_name, length] }
    q = queue.Queue()
    for name in workflow.start_functions:
        q.put(workflow.nodes[name])#注意q
        dist_vec[name] = [workflow.nodes[name].runtime, 0] #记录入度为0的函数运行时间
        prev_vec[name] = [] #入度为0的函数没有前驱节点
    while q.empty() is False:
        node = q.get()
        pre_dist = dist_vec[node.name] #这个prev_dist返回啥
        prev_name = node.name #前驱名字
        for index in range(len(node.next)):#node.next表示它的后续节点
            next_node = workflow.nodes[node.next[index]] #next_node是后续节点
            w = node.nextDis[index] #todo:这个nextDis还不是很理解
            #w是一个运行时间
            print('\n*********before w:',w,'*********')
            next_node_name = next_node.name #next_node的函数名
            if next_node_name in find_set(prev_name, group_set):
                w = w / config.NET_MEM_BANDWIDTH_RATIO
            print('*********after w:',w,'*********\n')
            ###理解:dist_vec的key为函数名，value是一个list,记为l,l[0]记录着执行完这个函数的需要的时间
            ###pre_dist[0]表示这个函数前驱节点的运行时间
            ###todo:l[0]是这个函数最终执行完的时间，
            ###比如说A->B,A执行完的时间为0.2s,A将数据给B的时间是0.3秒，B执行完的时间为0.4秒，此时l[0] = 0.2 + 0.3 + 0.4 = 0.9
            ###但是存在一个C->D->B,C运行时间为0.2，C->D为0.2,D运行时间为0.4，D->B为0.3，B运行时间为0.2
            ##则C->D->B，B的运行时间= 0.2 + 0.2 + 0.4 + 0.3 + 0.2 = 1.3
            ##取最大值，综上，这个workflow中B的运行时间为1.3
            ###todo 这个l[1]是什么还不是很理解
            if next_node.name not in dist_vec:
                dist_vec[next_node_name] = [pre_dist[0] + w + next_node.runtime, max(pre_dist[1], w)]
                prev_vec[next_node_name] = [prev_name, w]
            elif dist_vec[next_node_name][0] < pre_dist[0] + w + next_node.runtime:
                dist_vec[next_node_name] = [pre_dist[0] + w + next_node.runtime, max(pre_dist[1], w)]
                prev_vec[next_node_name] = [prev_name, w]
            elif dist_vec[next_node_name][0] == pre_dist[0] + w + next_node.runtime and max(pre_dist[1], w) > \
                    dist_vec[next_node_name][1]:
                dist_vec[next_node_name][1] = max(pre_dist[1], w)
                prev_vec[next_node_name] = [prev_name, w]
            in_degree_vec[next_node_name] -= 1 #in_degree_vec记录了每个函数的入度
            if in_degree_vec[next_node_name] == 0:
                q.put(next_node)
    return dist_vec, prev_vec
    ###wordcount的例子中:dist_vec = {'start': [0.02, 0], 'count': [0.6562745666503906, 0.5162745666503906], 'merge': [0.8187306213378907, 0.5162745666503906]}
#todo(lambda):这个函数可能需要我修改
def mergeable(node1, node2, group_set, workflow: component.workflow, write_to_mem_nodes, node_info):
    global mem_usage, max_mem_usage, group_ip, group_scale
    node_set1 = find_set(node1, group_set)

    # same set?
    if node2 in node_set1: # same set
        return False
    node_set2 = find_set(node2, group_set)

    # group size no larger than GROUP_LIMIT
    if len(node_set1) + len(node_set2) > config.GROUP_LIMIT:
        return False

    # meet scale requirement?
    new_node_info = node_info.copy()
    node_set1_scale = group_scale[node_set1] #记录多少容器数
    node_set2_scale = group_scale[node_set2] 
    new_node_info[group_ip[node_set1]] += node_set1_scale #todo:为什么加
    new_node_info[group_ip[node_set2]] += node_set2_scale
    best_fit_addr, best_fit_scale = None, 10000000
    #x寻找地址
    #这里好像找到一个主机的scale满足需求就可以
    for addr in new_node_info:
        if new_node_info[addr] >= node_set1_scale + node_set2_scale and new_node_info[addr] < best_fit_scale:
            best_fit_addr = addr
            best_fit_scale = new_node_info[addr]
    if best_fit_addr is None:
        print('Hit scale threshold', node_set1_scale, node_set2_scale)
        return False

    # check memory limit    
    if node1 not in write_to_mem_nodes:
        current_mem_usage = workflow.nodes[node1].nextDis[0] * config.NETWORK_BANDWIDTH #node1 记录需要的内存使用
        if mem_usage + current_mem_usage > max_mem_usage: # too much memory consumption
            print('Hit memory consumption threshold')
            return False
        mem_usage += current_mem_usage 
        write_to_mem_nodes.append(node1) #如果node1在内存访问内，就可以写入,即数据访问依赖内存，而不是couchdb

    # merge sets & update scale
    new_group_set = (*node_set1, *node_set2) #todo(lambda):针对情况更复杂的yaml可能需要我理解

    group_set.append(new_group_set)
    group_ip[new_group_set] = best_fit_addr ###! 这组group_set在best_fir_addr机器上运行吗
    node_info[best_fit_addr] -= node_set1_scale + node_set2_scale #更新best_fit_addr的空闲容器数
    group_scale[new_group_set] = node_set1_scale + node_set2_scale #更新group_scale[new_group_set]使用的容器数

    node_info[group_ip[node_set1]] += node_set1_scale
    node_info[group_ip[node_set2]] += node_set2_scale
    group_set.remove(node_set1) #todo:还需理解
    group_set.remove(node_set2) #todo:还需理解
    group_ip.pop(node_set1) #todo:还需理解
    group_ip.pop(node_set2) #todo:还需理解
    group_scale.pop(node_set1) #todo:还需理解
    group_scale.pop(node_set2) #todo:还需理解__len__ = {int} 2
    return True

def merge_path(crit_vec, group_set, workflow: component.workflow, write_to_mem_nodes, node_info):
    for edge in crit_vec:
        print('\n***edge[1][0]:',edge[1][0], "****and edge[0]",edge[0],'******\n')
        if mergeable(edge[1][0], edge[0], group_set, workflow, write_to_mem_nodes, node_info):
            return True
    return False


def get_longest_dis(workflow, dist_vec):
    dist = 0
    node_name = ''
    for name in workflow.nodes:
        if dist_vec[name][0] > dist:
            dist = dist_vec[name][0]
            node_name = name
    return dist, node_name

#todo:这个函数得好好理解
def grouping(workflow: component.workflow, node_info):

    # initialization: get in-degree of each node
    group_set = list()
    critical_path_functions = set()
    write_to_mem_nodes = []
    in_degree_vec = init_graph(workflow, group_set, node_info)

    while True:

        # break if every node is in same group
        if len(group_set) == 1:
            break

        # topo dp: find each node's longest dis and it's predecessor
        dist_vec, prev_vec = topo_search(workflow, in_degree_vec.copy(), group_set)
        crit_length, tmp_node_name = get_longest_dis(workflow, dist_vec) #得到workflow最长的运行时间，tmp_node_name为最后执行完的函数
        ###todo(lambda):得到这个函数名字，到时候可以给start_function发消息，让它们终止
        ###todo(lambda):tmp_node_name必须知道satrt_function在哪些机器上

        print('crit_length: ', crit_length) #关键路径的长度

        # find the longest path, edge descent sorted
        critical_path_functions.clear()
        crit_vec = dict()
        while tmp_node_name not in workflow.start_functions:
            crit_vec[tmp_node_name] = prev_vec[tmp_node_name]
            tmp_node_name = prev_vec[tmp_node_name][0]
        crit_vec = sorted(crit_vec.items(), key=lambda c: c[1][1], reverse=True) #todo: why sort
        for k, v in crit_vec:
            critical_path_functions.add(k)
            critical_path_functions.add(v[0])

        # if can't merge every edge of this path, just break
        if not merge_path(crit_vec, group_set, workflow, write_to_mem_nodes, node_info):
            break
    return group_set, critical_path_functions

# define the output destination at function level, instead of one per key/file
def get_type(workflow, node, group_detail):
    not_in_same_set = False
    in_same_set = False
    for next_node_name in node.next:
        next_node = workflow.nodes[next_node_name]
        node_set = find_set(next_node.name, group_detail) 
        if node.name not in node_set:
            not_in_same_set = True
        else:
            in_same_set = True
    if not_in_same_set and in_same_set:
        return 'DB+MEM'
    elif in_same_set:
        return 'MEM'
    else:
        return 'DB'

def get_max_mem_usage(workflow: component.workflow):
    global max_mem_usage
    for name in workflow.nodes:
        if not name.startswith('virtual'):
            max_mem_usage += (1 - config.RESERVED_MEM_PERCENTAGE - workflow.nodes[name].mem_usage) * config.CONTAINER_MEM * workflow.nodes[name].split_ratio
    return max_mem_usage

###存在DB里面
def save_grouping_config(workflow: component.workflow, node_info, info_dict, info_raw_dict, critical_path_functions):
    repo = repository.Repository(workflow.workflow_name)
    repo.save_function_info(info_dict, workflow.workflow_name + '_function_info') #把info_dict保存在workflow.workflow_name+"_function_info"的couchdb中
    repo.save_function_info(info_raw_dict, workflow.workflow_name + '_function_info_raw')
    repo.save_basic_input(workflow.global_input, workflow.workflow_name + '_workflow_metadata')
    repo.save_start_functions(workflow.start_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_foreach_functions(workflow.foreach_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_merge_functions(workflow.merge_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_all_addrs(list(node_info.keys()), workflow.workflow_name + '_workflow_metadata')
    repo.save_critical_path_functions(critical_path_functions, workflow.workflow_name + '_workflow_metadata')

# def query(workflow: component.workflow, group_detail: List):
#     total = 0
#     merged = 0
#     for name, node in workflow.nodes.items():
#         for next_node_name in node.next:
#             total = total + 1
#             merged_edge = False
#             for s in group_detail:
#                 if name in s and next_node_name in s:
#                     merged_edge = True
#             if merged_edge:
#                 merged = merged + 1
#     return merged, total

def get_grouping_config(workflow: component.workflow, node_info_dict):

    global max_mem_usage, group_ip

    # grouping algorithm
    max_mem_usage = get_max_mem_usage(workflow)
    # print('max_mem_usage', max_mem_usage)
    group_detail, critical_path_functions = grouping(workflow, node_info_dict) #图调度器，切割图
    ###! todo(lambda) 12-10更新，可以暂时将grouping当做黑盒来用
    ###! todo(lambda) 12-10更新，grouping算法就是将workflow切割成一个个子图
    print(group_detail)
    
    # print(query(workflow, group_detail))

    # building function info: both optmized and raw version
    ip_list = list(node_info_dict.keys())
    function_info_dict = {}
    function_info_raw_dict = {}
    for node_name in workflow.nodes:
        node = workflow.nodes[node_name] #函数节点
        to = get_type(workflow, node, group_detail) #记录这个node的存储数据格式
        ##这个函数节点的输出存在内存里还是存在数据库，或者内存和数据库都有
        #! todo(lambda)更新:我这里一律采用hoplite存储，可能需要改动,也就是to为MEM
        ip = group_ip[find_set(node_name, group_detail)] #返回值ip记录函数node_name在哪个函数上运行
        function_info = {'function_name': node.name, 'runtime': node.runtime, 'to': to, 'ip': ip,
                         'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
                         #?workflow.parent_cnt[node.name]返回一个大于等于0的整数
                         #todo:node.conditions还是不太懂
        function_info_raw = {'function_name': node.name, 'runtime': node.runtime, 'to': 'DB', 'ip': ip_list[hash(node.name) % len(ip_list)],
                             'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
        function_input = dict()
        function_input_raw = dict()
        for arg in node.input_files:
            #记录这个函数节点的输入文件
            function_input[arg] = {'size': node.input_files[arg]['size'],
                                   'function': node.input_files[arg]['function'],
                                   'parameter': node.input_files[arg]['parameter'],
                                   'type': node.input_files[arg]['type']}
            function_input_raw[arg] = {'size': node.input_files[arg]['size'],
                                       'function': node.input_files[arg]['function'],
                                       'parameter': node.input_files[arg]['parameter'],
                                       'type': node.input_files[arg]['type']}
        function_output = dict()
        function_output_raw = dict()
        #!记录这个函数节点的输出
        for arg in node.output_files:
            function_output[arg] = {'size': node.output_files[arg]['size'], 'type': node.output_files[arg]['type']}
            function_output_raw[arg] = {'size': node.output_files[arg]['size'], 'type': node.output_files[arg]['type']}
        function_info['input'] = function_input
        function_info['output'] = function_output
        function_info['next'] = node.next
        function_info_raw['input'] = function_input_raw
        function_info_raw['output'] = function_output_raw
        function_info_raw['next'] = node.next
        function_info_dict[node_name] = function_info#function_info_dict记录每个函数的函数信息
        ###包括函数名，运行时间，在哪台机器上运行，父亲节点的个数，输出的数据以什么方式存在faasstore
        ###todo:我这里需要修改，因为输出的数据都存在内存里
        function_info_raw_dict[node_name] = function_info_raw
    
    # if successor contains 'virtual', then the destination of storage should be propagated
    ###todo:这里不是很懂
    for name in workflow.nodes:
        for next_name in workflow.nodes[name].next:
            if next_name.startswith('virtual'):
                if function_info_dict[next_name]['to'] != function_info_dict[name]['to']:
                    function_info_dict[name]['to'] = 'DB+MEM'
    #? 这里的node_info_dict表示工作节点机器的ip:port以及可以容纳的容器数量
    return node_info_dict, function_info_dict, function_info_raw_dict, critical_path_functions

if __name__ == '__main__':
    """
    if len(sys.argv) <= 1:
        print('usage: python3 grouping.py <workflow_name>, ...')
    """
    # get node info
    ##todo一些消息
    node_info_list = yaml.load(open('node_info.yaml'), Loader=yaml.FullLoader)
    node_info_dict = {}
    for node_info in node_info_list['nodes']:
        print('node_info_',node_info)
        node_info_dict[node_info['worker_address']] = node_info['scale_limit'] * 0.8
    print('node_info_dict',node_info_dict)
    
    workflow_pool = ['wordcount']
    #workflow_pool = sys.argv[1:]
    for workflow_name in workflow_pool:
        print('workflow_namae',workflow_name)
        workflow = test_parse_yaml.parse(workflow_name)  #解析文件，返回的是整个workflow的函数
        node_info, function_info, function_info_raw, critical_path_functions = get_grouping_config(workflow, node_info_dict)
        save_grouping_config(workflow, node_info, function_info, function_info_raw, critical_path_functions)
    