import yaml
import component
import config
from collections import defaultdict

yaml_file_addr = config.WORKFLOW_YAML_ADDR

def parse(workflow_name):
    data = yaml.load(open(yaml_file_addr[workflow_name]), Loader=yaml.FullLoader)
    print(data)
    global_input = dict()
    start_functions = []
    nodes = dict()
    parent_cnt = dict()
    foreach_functions = set()
    merge_funtions = set()
    total = 0
    
    next_function_node = defaultdict(list) #?记录某个函数的后续节点是什么,一个函数可能有多个后续节点
    ##!注:这里的后续节点注包括直接相连的边，比如说A->B,B->C,B->D,此时A的后续节点只有B
    #? B的后续节点有C和D
    prev_function_node  =dict() # defaultdict(list) ##!记录某个函数的前驱节点是什么，
    #? 此时C和D的后续节点为B

    ###todo gloabl_input还需理解
    if 'global_input' in data:
        for key in data['global_input']:
            parameter = data['global_input'][key]['value']['parameter']
            #global_input[parameter] = data['global_input'][key]['size']
            global_input[key] = data['global_input'][key]['size'] #为科学计算服务
    functions = data['functions']
    parent_cnt[functions[0]['name']] = 0 
    for function in functions:
        #print('*********functon:',function,'\n')
        name = function['name'] #?name为某个函数名字
        print('------------name:----------',name) #这个应该是start / count /merge
        source = function['source']
        runtime = function['runtime']
        input_files = dict()
        output_files = dict()
        next = list()
        nextDis = list()
        send_byte = 0
        if 'input' in function:
            for key in function['input']:
                print('**********start********')
                #当'input'在funcion有时，表示这个function需要外部输入，即这个function不是DAG的起始点函数
                print('key:',key,'\n\n')
                print('function:', function['input'][key]['value']['function'],'\n') #记录这个input来着哪个函数
                print('parameter:', function['input'][key]['value']['parameter']) #记录参数，在wordcount是一个filename
                print('size:', function['input'][key]['size'])#记录大小
                print('arg:', key)#这个未知
                print('type:', function['input'][key]['type']) #记录type
                print('*********end*************\n\n\n')
                input_files[key] = {'function': function['input'][key]['value']['function'],
                                    'parameter': function['input'][key]['value']['parameter'],
                                    'size': function['input'][key]['size'], 'arg': key,
                                    'type': function['input'][key]['type']}
                ###todo:这里记录input_files[key]是干啥
                #!12-10更新，input_file[key]记录某个函数的输入
                #!12-10 更新，这个函数的输入存在两种情况
                #!入度为0，它的输入来着外部输入
                #! 入度不为0，它的输入来自它的前驱节点
        if 'output' in function:
            print('the function has output:',name,'\n\n')
            for key in function['output']:
                output_files[key] = {'size': function['output'][key]['size'], 'type': function['output'][key]['type']} #这个是每个函数的输出
                send_byte += function['output'][key]['size']
        send_time = send_byte / config.NETWORK_BANDWIDTH
        conditions = list()
        #看function是否存在'next'
        #目前只有count和start有next
        #表示它们有后续节点，
        ###在wordcount的workflow中，是start->count->merge
        ##todo:这里需要记录一些东西
        ###todo:比如说记录start的next为count,count的后续节点为merge,我需要增加的点
        ###todo:也可能需要记录count的前驱节点为start,merge的前驱节点为count
        ###todo:这是我需要加上的点
        if 'next' in function:
            foreach_flag = False
            if function['next']['type'] == 'switch':
                conditions = function['next']['conditions']
            elif function['next']['type'] == 'foreach':
                foreach_flag = True
            for n in function['next']['nodes']:
                ###这一步记录next有什么函数，因为一个函数的后续节点可能有多个
                #? 记录前驱节点和后续节点
                #?在count中，它的function['next']['nodes] = merge
                next_function_node[name].append(n) ###todo:这里用set是不是更合适？(by lambda,或许需要修改)
                prev_function_node[n] = name #?每个节点的前驱节点只有一个


                if name in foreach_functions:
                    merge_funtions.add(n)
                ###todo:加入merge_function是不是很理解
                if foreach_flag:
                    foreach_functions.add(n) #把n加入foreach_functions
                next.append(n)#next是一个list,可以重复加入相同的 数据,next记录这个函数的后续节点
                ###n是一个函数名
                nextDis.append(send_time)#todo:这里的send_time加入nextDis还是不理解
                ###存在next,表示它有后续节点
                ###todo 12-09, nextDis是什么，
                #! send_time是发送数据的时间
                ##todo:不是很理解，parent_cnt[n]这里是记录这个函数n有多少个父节点
                ###todo:在FaasFlow的设计中，只有n所有的父节点都运行完了，n才可以运行
                ###*
                if n not in parent_cnt:
                    parent_cnt[n] = 1
                else:
                    parent_cnt[n] = parent_cnt[n] + 1
        current_function = component.function(name, [], next, nextDis, source, runtime,
                                              input_files, output_files, conditions)
        #得到current_function，它记录了它的next节点有哪些，以及输入输出文件，
        ###todo:conditions还不是很理解(by lambda)
        if 'scale' in function:
            current_function.set_scale(function['scale'])
        if 'mem_usage' in function:
            current_function.set_mem_usage(function['mem_usage'])
        if 'split_ratio' in function:
            current_function.set_split_ratio(function['split_ratio'])
        total = total + 1 #! total记录了整个workflow有几个节点
        nodes[name] = current_function #记录当前这个函数name的current_function
    for name in nodes:
        print('\n*********name:',name,'\n')
        if name not in parent_cnt or parent_cnt[name] == 0:
            parent_cnt[name] = 0
            start_functions.append(name) #找到哪些没有前驱节点的，即该节点的入度为0
            #! start_functions是一个list,可以有多个
        for next_node in nodes[name].next:
            print('\n***next_node:',next_node,'\n')
            nodes[next_node].prev.append(name) #?记录每个节点的前驱节点函数
    return component.workflow(workflow_name, start_functions, nodes, global_input, total, parent_cnt, foreach_functions, merge_funtions)



