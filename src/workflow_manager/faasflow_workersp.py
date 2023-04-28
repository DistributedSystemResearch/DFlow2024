import sys
import logging
import time

import repository
import gevent
import gevent.lock
from typing import Any, Dict, List
import requests
 
sys.path.append('../function_manager')
from function_manager import FunctionManager

repo = repository.Repository()
class FakeFunc:
    def __init__(self, req_id: str, func_name: str):
        self.req_id = req_id
        self.func = func_name

    def __getattr__(self, name: str):
        return repo.fetch(self.req_id, name)


def cond_exec(req_id: str, cond: str) -> Any:
    if cond.startswith('default'):
        return True

    values = {}
    res = None
    while True:
        try:
            res = eval(cond, values)
            break
        except NameError as e:
            name = str(e).split("'")[1]
            values[name] = FakeFunc(req_id, name)
    return res

class WorkflowState:
    def __init__(self, request_id: str, all_func: List[str]):
        self.request_id = request_id
        self.lock = gevent.lock.BoundedSemaphore() # guard the whole state

        self.executed: Dict[str, bool] = {} #!,12-12,记录这个函数是否正在运行，str对应函数名，true表示在运行，false表示没有
        self.parent_executed: Dict[str, int] = {} #str表示函数名，int为其父节点个数
        for f in all_func:
            self.executed[f] = False
            self.parent_executed[f] = 0

min_port = 20000

# mode: 'optimized' vs 'normal'
#还是得好好理解
class WorkerSPManager:
    def __init__(self, host_addr: str, workflow_name: str, data_mode: str, function_info_addr: str):
        global min_port

        self.lock = gevent.lock.BoundedSemaphore() # guard self.states
        self.host_addr = host_addr #! 这个是主机地址
        self.workflow_name = workflow_name #! 工作流名字
        self.states: Dict[str, WorkflowState] = {} #?存取状态，见论文图6
        self.function_info: Dict[str, dict] = {} #? 函数信息，见论文图6

        self.data_mode = data_mode
        ###! info_db表示从哪个couchdb取function_info 
        if data_mode == 'optimized':
            self.info_db = workflow_name + '_function_info' 
        else:
            self.info_db = workflow_name + '_function_info_raw'
        self.meta_db = workflow_name + '_workflow_metadata'

        self.foreach_func = repo.get_foreach_functions(self.meta_db)
        self.merge_func = repo.get_merge_functions(self.meta_db)
        self.func = repo.get_current_node_functions(self.host_addr, self.info_db) #todo:12-11得到函数，这个是一个list
        
        self.function_manager = FunctionManager(function_info_addr, min_port)#todo:12-11,function_info_addr要理解
        min_port += 5000

    # return the workflow state of the request
    ##todo:这个不是很理解
    def get_state(self, request_id: str) -> WorkflowState:
        self.lock.acquire()
        if request_id not in self.states:
            self.states[request_id] = WorkflowState(request_id, self.func)
        state = self.states[request_id]
        self.lock.release()
        return state
    
    def del_state_remote(self, request_id: str, remote_addr: str):
        url = 'http://{}/clear'.format(remote_addr)
        requests.post(url, json={'request_id': request_id, 'workflow_name': self.workflow_name})

    # delete state
    def del_state(self, request_id: str, master: bool):
        logging.info('delete state of: %s', request_id)
        self.lock.acquire()
        if request_id in self.states:
            del self.states[request_id]
        self.lock.release()
        if master:
            jobs = []
            addrs = repo.get_all_addrs(self.meta_db)
            for addr in addrs:
                if addr != self.host_addr:
                    jobs.append(gevent.spawn(self.del_state_remote, request_id, addr))
            gevent.joinall(jobs)

    # get function's info from database
    # the result is cached
    ###todo:12-11,这里的注释是从数据库得到函数信息，我还是暂时不理解
    def get_function_info(self, function_name: str) -> Any:
        if function_name not in self.function_info:
            self.function_info[function_name] = repo.get_function_info(function_name, self.info_db)
        return self.function_info[function_name]

    # trigger the function when one of its parent is finished
    # function may run or not, depending on if all its parents were finished
    # function could be local or remote
    ###todo-12-11,trigger_function的参数state还是不理解
    def trigger_function(self, state: WorkflowState, function_name: str, no_parent_execution = False) -> None:
        func_info = self.get_function_info(function_name) #函数信息
        ###!更新:self.get_function_info(function_name)得到这个函数的信息，见grouping.py的
        """
        !
                function_info = {'function_name': node.name, 'runtime': node.runtime, 'to': to, 'ip': ip,
                         'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
                         #?workflow.parent_cnt[node.name]返回一个大于等于0的整数
        !                 #todo:node.conditions还是不太懂
        这个funcion_info记录了其运行时间，ip为在哪台机器执行，to是存储格式，存在数据库还是本地内存，
        parent_cnt是记录其前驱节点个个数，workflow.parent_cnt[node.name]是一个int数据
        node.name是这个节点的名字，?
        """
        ####
        if func_info['ip'] == self.host_addr: 
            # function runs on local
            ###! 12-11,当func_info['ip']为self.host_addr时，表示这个函数在这台机器运行
            ###!如果不等于，表示这个函数在其它机器运行
            ###todo:12-11我这里需要更新，采用我自己的设计
            ###?12-11这个函数A运行后，其在DAG直接后续节点函数(记为函数B,函数C)也就是next也要开始运行，当B C需要A的输出后,自动Block住
            ###?12-11,知道A的数据生成
            self.trigger_function_local(state, function_name, no_parent_execution)
        else:
            # function runs on remote machine
            #? 12-11,function_info['ip']表示这个函数需要在这个ip上执行
            self.trigger_function_remote(state, function_name, func_info['ip'], no_parent_execution)
        ###todo(lambda:),我自己的实现，找到函数的后续节点，也启动
    
    def trigger_function_lambda(self, state: WorkflowState, function_name: str, no_parent_execution = False) ->None:
        func_info = self.get_function_info(function_name)
        jobs = [] 
        if func_info['ip'] == self.host_addr:
            job = gevent.spawn(self.trigger_function_local_lambda,state,function_name,no_parent_execution) #lambda，要增加我自己的函数
            jobs.append(job)
        else: #不在这台机器上运行
            job= gevent.spawn(self.trigger_function_remote_lambda,state,func_name,func_info['ip'],no_parent_execution)
            jobs.append(job)

        #todo,12-13这里需要增加的一个逻辑:当这个函数为状态为running时，才可以启动后续节点
        ####todo 12-13,running有两种情况:1)函数没有前驱节点，这个时候必可以启动后续节点
        ###2)该函数的前驱节点运行完了，这个时候可以启动后续节点
        ###存在的问题:一个函数先是发到请求队列里，然后请求队列里拿到这个函数，然后在docker里面运行
        ###按照hoplite的逻辑，当它需要前驱节点的数据时，如果这个时候前驱节点的数据还没生成，则自动block住，这个时候函数的状态应该是
        ###!blocked,但是怎么知道函数是不是block住了？因为这个时候函数在docker里运行哈
        for func in func_info['next']:
            job = gevent.spawn(self.trigger_function,state,func)
            jobs.append(job)
        gevent.joinall(jobs)


    def trigger_function_local_lambda(self, state: WorkflowState, function_name: str, no_parent_execution = False)->None:
        return None ##todo:12-13我要增加自己的逻辑

        
    def trigger_function_remote_lambda(self, state: WorkflowState, function_name: str, no_parent_execution = False)->None:
        return None ###todo,12-13,增加自己的逻辑


    # trigger a function that runs on local
    def trigger_function_local(self, state: WorkflowState, function_name: str, no_parent_execution = False) -> None:
        logging.info('trigger local function: %s of: %s', function_name, state.request_id)
        state.lock.acquire()
        if not no_parent_execution:
            ###? 12-11,当no_parent_execution为false时,增加这个函数的父节点个数，表示这个节点入度不为0
            state.parent_executed[function_name] += 1
        runnable = self.check_runnable(state, function_name)#检查状态是否都运行完了
        # remember to release state.lock
        if runnable:
            state.executed[function_name] = True #! 当state.executed[function_name]=true时，表示它现在在运行中
            state.lock.release()
            self.run_function(state, function_name)
        else:
            state.lock.release()

    # trigger a function that runs on remote machine
    ###给其它机器发消息，让这个机器运行这个函数
    def trigger_function_remote(self, state: WorkflowState, function_name: str, remote_addr: str, no_parent_execution = False) -> None:
        logging.info('trigger remote function: %s on: %s of: %s', function_name, remote_addr, state.request_id)
        remote_url = 'http://{}/request'.format(remote_addr)
        data = {
            'request_id': state.request_id,
            'workflow_name': self.workflow_name,
            'function_name': function_name,
            'no_parent_execution': no_parent_execution,
        }
        response = requests.post(remote_url, json=data)
        response.close()

    # check if a function's parents are all finished
    #todo 怎么检查，还需理解
    def check_runnable(self, state: WorkflowState, function_name: str) -> bool:
        info = self.get_function_info(function_name)
        #! 12-11,info是这个函数对应的函数信息，包括ip，父母个数
        """
        !
                function_info = {'function_name': node.name, 'runtime': node.runtime, 'to': to, 'ip': ip,
                         'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
                         #?workflow.parent_cnt[node.name]返回一个大于等于0的整数
        !                 #todo:node.conditions还是不太懂
        这个funcion_info记录了其运行时间，ip为在哪台机器执行，to是存储格式，存在数据库还是本地内存，
        parent_cnt是记录其前驱节点个个数，workflow.parent_cnt[node.name]是一个int数据
        node.name是这个节点的名字，?
        """
        ##todo:12-11,state还不是很理解，state.parent_exected[function_name]表示这个函数的父节点运行完的数量
        ###todo:12-11,info_parent['parent_cnt']表示这个函数有多少个父节点
        ###todo:按FaaSFlow的设计，主要当这个函数的所有父节点都运行完了之后，它才可以开始运行
        ###todo(lambda):StoneFree的设计:目前当这个函数的父节点启动后，该函数也会启动运行，只有需要父节点的数据时才会block住
        ###todo(lambda):所有这里需要记录一个状态，当这个函数有多个父节点时，某个父节点启动了这个函数，这个函数的设一个标记位，假设为runnable
        ###todo(lambda),然后这个函数的其它父节点想启动这个函数时，先检查这个标志位，如果为runnable,就直接return 
        return state.parent_executed[function_name] == info['parent_cnt'] and not state.executed[function_name]
        #!(一个问题)12-11:state.executed[function_name]表示这个函数是否在运行中
    # run a function on local
    def run_function(self, state: WorkflowState, function_name: str) -> None:
        logging.info('run function: %s of: %s', function_name, state.request_id)
        # end functions
        if function_name == 'END':
            return

        info = self.get_function_info(function_name)#得到函数信息
        # switch functions
        if function_name.startswith('virtual'): #todo what is this 
            self.run_switch(state, info)
            return # do not need to check next
        
        if function_name in self.foreach_func:
            self.run_foreach(state, info)
        elif function_name in self.merge_func:
            self.run_merge(state, info)
        else: # normal functions
            self.run_normal(state, info)
        
        # trigger next functions
        ###! 12-12, 当这个函数执行完了,触发下一个函数
        jobs = [
            gevent.spawn(self.trigger_function, state, func)
            for func in info['next']
        ]
        gevent.joinall(jobs)
    ##todo,12-13代码修改
    
    ##todo(12-11):这里不是很理解
    def run_switch(self, state: WorkflowState, info: Any) -> None:
        for i, next_func in enumerate(info['next']):
                cond = info['conditions'][i]
                if cond_exec(state.request_id, cond):
                    self.trigger_function(state, next_func)
                    break
    ###并行执行
    ###? 12-11,StoneFree设计:按FaasFlow的设计，run_foreach是某个父节点函数执行完了后，然后它有很多后续节点函数
    ###? 12-11,这些后续节点函数然后开始执行，按我的设计，当父节点开始执行的时候，这些后续节点也可以开始执行了，只是需要父节点的数据时
    ###? 12-11 才会block,不过这些函数都是在一台机器上运行，所以不用考虑机器上是的有这么多容器可以支持这些函数运行
    ###! 设计方案:父节点执行的时候，同时启动其直接后续节点，让其开始运行，当后续节点需要A的数据时，才会block住，等A生成数据
    ###! 其实这就是类似一个MPI_Broadcast
    ###todo(lambda),12-11,python无法支持多线程运行，所以可以做到多个后续节点和父节点同时运行吗？或许需要采用多进程到方式
    def run_foreach(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        all_keys = repo.get_keys(state.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
        foreach_keys = []  # ['split_keys', 'split_keys_2']
        for arg in info['input']:
            if info['input'][arg]['type'] == 'key':
                foreach_keys.append(info['input'][arg]['parameter'])
        jobs = []
        for i in range(len(all_keys[foreach_keys[0]])):
            keys = {}  # {'split_keys': '1', 'split_keys_2': '2'}
            for k in foreach_keys:
                keys[k] = all_keys[k][i]
            jobs.append(gevent.spawn(self.function_manager.run, info['function_name'], state.request_id,
                                     info['runtime'], info['input'], info['output'],
                                     info['to'], keys))
        gevent.joinall(jobs)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    ###todo,12-11,run_merge也不是很理解
    def run_merge(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        all_keys = repo.get_keys(state.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
        self.function_manager.run(info['function_name'], state.request_id,
                             info['runtime'], info['input'], info['output'],
                             info['to'], all_keys)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    def run_normal(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        self.function_manager.run(info['function_name'], state.request_id,
                             info['runtime'], info['input'], info['output'],
                             info['to'], {})#.
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    def clear_mem(self, request_id):
        repo.clear_mem(request_id)
    
    def clear_db(self, request_id):
        repo.clear_db(request_id)