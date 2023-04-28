from typing import Dict


class function:
    def __init__(self, name, prev, next, nextDis, source, runtime, input_files, output_files, conditions):
        self.name = name
        self.prev = prev #前驱节点
        self.next = next #后续节点
        self.nextDis = nextDis
        self.source = source
        self.runtime = runtime
        self.input_files = input_files
        self.output_files = output_files
        self.conditions = conditions
        self.scale = 0
        self.mem_usage = 0
        self.split_ratio = 1
    
    def set_scale(self, scale):
        self.scale = scale

    def set_mem_usage(self, mem_usage):
        self.mem_usage = mem_usage
    
    # foreach: multiple container in one workflow
    def set_split_ratio(self, split_ratio):
        self.split_ratio = split_ratio


class workflow:
    def __init__(self, workflow_name, start_functions, nodes: Dict[str, function], global_input, total, parent_cnt, foreach_functions, merge_functions):
        self.workflow_name = workflow_name #工作流名字
        self.start_functions = start_functions #该工作流可以一开始就启动的函数
        self.nodes = nodes  # dict: {name: function()} #节点函数，该节点定义好了前驱后驱，输入输出
        self.global_input = global_input #全局输入
        self.total = total
        self.parent_cnt = parent_cnt  # dict: {name: parent_cnt} 记录节点的父亲节点有几个，key为函数名，value为int
        self.foreach_functions = foreach_functions #todo 还需要理解
        self.merge_functions = merge_functions #todo 还需要理解