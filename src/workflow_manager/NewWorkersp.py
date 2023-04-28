import sys
import logging
import time
import json
import repository
import gevent
import gevent.lock
from typing import Any, Dict, List
import requests
 
sys.path.append('../function_manager')
from function_manager import FunctionManager

import sys
sys.path.append("..")
from my_log import log

repo = repository.Repository()
class FakeFunc:
    def __init__(self, req_id: str, func_name: str):
        self.req_id = req_id
        self.func = func_name

    # def __getattr__(self, name: str):
    #     return repo.fetch(self.req_id, name)


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
        self.status:Dict[str,str] = {} 
        self.record_funcs:Dict[str,bool] = {} #记录子孙节点，比如说A->B,C->B,B->D,B->E,然后A C 在同一台机器，A运行完了，要启动D和E,C运行完了要启动D E
        #用record_funcs记录只启动一次D 和E
        #!记录整个workflow每一个节点的状态
        ###!这个self.status的key为这个workflow中每一个函数的函数名
        ###!value为这个节点的每一个函数的状态
        ###!初始时，为running->表示正在运行，可以起后续节点
        ###!blocked->表示暂时不能起后续节点
        ###!Done->表示节点已经结束完成了，假设其后续节点还有后续节点，比如说A->B,B-C,B->D,A结束了，就要起B、C和D
        for f in all_func:
            self.executed[f] = False
            self.parent_executed[f] = 0

min_port = 20000

# mode: 'optimized' vs 'normal'
#还是得好好理解
class WorkerSPManager:
    def __init__(self, host_addr: str, workflow_name: str, data_mode: str, function_info_addr: str):
        global min_port
        #print('WorkerSPManager,the workflow_name:')
        #print('WorkerSPManager','the workflow_name',workflow_name,' and function_info_addr:', function_info_addr)
        log.info('WorkerSPManager, the workflow_name:%s and  function_info_addr:%s',workflow_name,function_info_addr)
        #self.locks ={} #todo 增加细粒度锁，给workflow中的name增加细粒度锁
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
        print("self.info_db:",self.info_db)
        self.info_ip_db = workflow_name +  '_function_ip' #整个workflow的ip所在的数据库
        self.meta_db = workflow_name + '_workflow_metadata'

        self.foreach_func = repo.get_foreach_functions(self.meta_db)
        self.merge_func = repo.get_merge_functions(self.meta_db)
        self.func = repo.get_current_node_functions(self.host_addr, self.info_db) #todo:12-11得到函数，这个是一个list
        
        self.func_ip = repo.get_function_ip(self.info_ip_db,workflow_name)
        #print('self.func_ip:',self.func_ip) #把这个打印出来，我的推测应该是一个workflow中的所以函数名及其ip:port
        #log.info("self.func_ip:%s",self.func_ip)
        #log.info('workersp,the function_info_addr:%s',function_info_addr)
        self.function_manager = FunctionManager(function_info_addr, min_port,self.host_addr)#todo:12-11,function_info_addr要理解
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
        log.info('delete state of: %s', request_id)
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
    ###update 12-14，没啥不好理解的看grouping就知道了
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
        func_info = self.get_function_info(function_name) #某个函数名的函数信息
        jobs = [] 
        log.info('1trigger  function lambda : %s of: %s on func_info:%s' ,function_name,state.request_id,func_info)

        func_ip = self.func_ip[function_name] #减少读数据库的机会
        log.info('2trigger  function lambda : %s of: %s on func_ip:%s \n func_info:%s\n' ,function_name,state.request_id,func_ip,func_info) #here is important
        print('trigger  function lambda :',function_name, ' of:',state.request_id, 'on func_ip:',func_ip ,' \n func_info:\n',func_info)
        
        #self.func_ip的key是函数名，value是ip
        if func_ip == self.host_addr:
            job = gevent.spawn(self.trigger_function_local_lambda,state,function_name,func_ip,no_parent_execution) #lambda，要增加我自己的函数
            jobs.append(job)
        else: #不在这台机器上运行
            job= gevent.spawn(self.trigger_function_remote_lambda,state,function_name,func_ip,no_parent_execution)
            jobs.append(job)

        #todo,12-13这里需要增加的一个逻辑:当这个函数为状态为running时，才可以启动后续节点
        ####todo 12-13,running有两种情况:1)函数没有前驱节点，这个时候必可以启动后续节点
        ###2)该函数的前驱节点运行完了，这个时候可以启动后续节点
        ###存在的问题:一个函数先是发到请求队列里，然后请求队列里拿到这个函数，然后在docker里面运行
        ###按照hoplite的逻辑，当它需要前驱节点的数据时，如果这个时候前驱节点的数据还没生成，则自动block住，这个时候函数的状态应该是
        ###!blocked,但是怎么知道函数是不是block住了？因为这个时候函数在docker里运行哈
        ###!一个疑问，gevent.spawn(self.trigger_function),这样是否可行？因为在trigger_function调用了gevent.spawn(self.trigger_function)
        ###! 这是递归调用吗
        ###这里要添加终止条件
        ###? 12-14更新,假设该节点没有前驱节点，直接起后续节点
        log.info("3trigger function lamdba:funct_info['prev']:%s and len(func_info['prev']):%s",func_info['prev'], len(func_info['prev']))
        print("trigger function lamdba:funct_info['prev']:",func_info['prev'] , " and len(func_info['prev']):", len(func_info['prev']))
        
        if len(func_info['prev']) == 0: ##TODO(error)
            for func in func_info['next']:
                #用细粒度锁是不是更好 todo
                #new_func_info = self.get_function_info(function_name)
                #func_ip = new_func_info[]

                log.info('4trigger function lambda:func:%s ',func)
                print('trigger function lambda:func: ',func)
                this_func_ip = self.func_ip[func]
                if this_func_ip == self.host_addr:
                    job = gevent.spawn(self.trigger_function_local_lambda,state,func,this_func_ip,no_parent_execution) #lambda，要增加我自己的函数
                    jobs.append(job)
                    #return None #TODO:这里需要更新
                else:
                    job= gevent.spawn(self.trigger_function_remote_lambda,state,func,this_func_ip,no_parent_execution)
                    jobs.append(job)
                """
                self.lock.acquire()
                if state.executed[func] == False:#表示之前函数没有启动过,
                    #因为可能存在A->C,B->C,A启动了C，B就不需要启动C了
                    state.executed[func] = True
                    job = gevent.spawn(self.trigger_function_lambda,state,func)
                    jobs.append(job)
                self.lock.release()
                """
            gevent.joinall(jobs)
        else:
            gevent.joinall(jobs)
    


    def trigger_function_local_lambda(self, state: WorkflowState, function_name: str, func_ip:str, no_parent_execution = False)->None:
        ##todo:12-13我要增加自己的逻辑
        ##update,12-14，A运行的时候直接运行B 
        state.lock.acquire()
        log.info("4.9 trigger_function_lambda,the function_name:%s and state.executed[%s]:%s",function_name,function_name ,state.executed[function_name])
        if state.executed[function_name] == False:
            state.executed[function_name] =True 
            state.lock.release()
            log.info('5trigger local function lambda : %s of: %s on func_ip:%s' , function_name, state.request_id,func_ip)
            print('trigger local function lambda ,the function_name:',function_name, ' and the func_ip:',func_ip)
            self.run_function_lambda(state,function_name,func_ip)
        else:
            state.lock.release()

     # run a function on local，正常运行一个函数
    def run_function_lambda(self, state: WorkflowState, function_name: str, func_ip:str) -> None:
        log.info('run function lambda: %s of: %s on func_ip:%s', function_name, state.request_id,func_ip)
        print('run function lambda, the function_name:', function_name ,' and func_ip:',func_ip)
        # end functions
        if function_name == 'END':
            return

        info = self.get_function_info(function_name)#得到函数名对应的函数信息
        # switch functions
        if function_name.startswith('virtual'): #todo what is this #todo(01-10,这个只适合video/illegal这两个benchmark)  
            self.run_switch_lambda(state, info,func_ip)
            return # do not need to check next
        
        if function_name in self.foreach_func:
            log.info('6run function lambda,this function_name:%s is in self.foreach_func:%s ',function_name ,self.foreach_func)
            print('run function lambda,this function_name:',function_name,' is in self.foreach_func:',self.foreach_func)
            self.run_foreach_lambda(state, info,func_ip)
        elif function_name in self.merge_func:
            log.info('7run function lambda,this function_name:%s is self.merge_func:%s',function_name,self.merge_func)
            print('run function lambda,this function_name:',function_name, '  is self.merge_func:',self.merge_func)
            self.run_merge_lambda(state, info,func_ip) #todo(01-10):这里可能需要修改
        else: # normal functions
            log.info('8run function lambda, this function_name:%s is normal function',function_name)
            print('run function lambda, this function_name:',function_name,' is normal function')
            self.run_normal_lambda(state, info,func_ip)

    ##todo(12-11):这里不是很理解
    ###todo(01-10) 不理解也没事,因为不会用到
    def run_switch_lambda(self, state: WorkflowState, info: Any, func_ip:str) -> None:
        return None #todo 12-14,这里需要我更新
        """
        for i, next_func in enumerate(info['next']):
                cond = info['conditions'][i]
                if cond_exec(state.request_id, cond):
                    self.trigger_function(state, next_func)#todo:这里需要更新
                    break
        """
    ###并行执行
    ###? 12-11,StoneFree设计:按FaasFlow的设计，run_foreach是某个父节点函数执行完了后，然后它有很多后续节点函数
    ###? 12-11,这些后续节点函数然后开始执行，按我的设计，当父节点开始执行的时候，这些后续节点也可以开始执行了，只是需要父节点的数据时
    ###? 12-11 才会block,不过这些函数都是在一台机器上运行，所以不用考虑机器上是的有这么多容器可以支持这些函数运行
    ###! 设计方案:父节点执行的时候，同时启动其直接后续节点，让其开始运行，当后续节点需要A的数据时，才会block住，等A生成数据
    ###! 其实这就是类似一个MPI_Broadcast
    ###todo(lambda),12-11,python无法支持多线程运行，所以可以做到多个后续节点和父节点同时运行吗？或许需要采用多进程的方式
    def run_foreach_lambda(self, state: WorkflowState, info: Any,func_ip:str) -> None:
        log.info('9run_foreach_lambda,\n the info:%s and func_ip:%s',info,func_ip)
        print('run_foreach_lambda,\nthe info:',info , '\n  and func_ip:', func_ip )
        start = time.time()
        foreach_keys = []  # ['split_keys', 'split_keys_2']
        for arg in info['input']:
            if info['input'][arg]['type'] == 'key':
                foreach_keys.append(info['input'][arg]['parameter'])
        jobs = []
        for i in range(1):#这里改成一个固定的数字，然后FaasFlow那里也改动
            keys = {}  # {'split_keys': '1', 'split_keys_2': '2'}
            # for k in foreach_keys:
            #     #keys[k] = all_keys[k][i] ##TODO(error)
            jobs.append(gevent.spawn(self.function_manager.run_lambda, info['function_name'], state.request_id,
                                     info['runtime'], info['my_input'], info['my_output'],
                                     info['to'], {},func_ip,self.workflow_name))
        gevent.joinall(jobs)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    ###todo,12-11,run_merge也不是很理解
    def run_merge_lambda(self, state: WorkflowState, info: Any,func_ip:str) -> None:
        start = time.time()
        #all_keys = repo.get_keys(state.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
        self.function_manager.run_lambda(info['function_name'], state.request_id,
                             info['runtime'], info['my_input'], info['my_output'],
                             info['to'], {}, func_ip,self.workflow_name) #FIXME 01-11(这里的all_keys干什么的)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})

    def run_normal_lambda(self, state: WorkflowState, info: Any, func_ip:str) -> None:
        start = time.time()
        #log.info('run normal_lambda,the function_name:%s',info['function_name'])

        #print('run normal_lambda,the info[unction_name]:',info['function_name'])
        log.info("10in run_normal_lambda,the workflow_name:%s and the function_name:%s and info['my_input']:%s \n and info['my_output']:%s\n" ,self.workflow_name,info['function_name'],info['my_input'], info['my_output'])
        # self.function_manager.run_lambda(info['function_name'], state.request_id,
        #                      info['runtime'], info['input'], info['output'],
        #                      info['to'], {},func_ip,self.workflow_name) #TODO(error) 

        self.function_manager.run_lambda(info['function_name'], state.request_id,
                             info['runtime'], info['my_input'], info['my_output'],
                             info['to'], {},func_ip,self.workflow_name) #TODO(error) 
        #FIXME
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})
    
     # trigger a function that runs on remote machine
    ###给其它机器发消息，让这个机器运行这个函数
    def trigger_function_remote_lambda(self, state: WorkflowState, function_name: str, remote_addr: str, no_parent_execution = False) -> None:
        log.info('11trigger remote function lambda: %s on: %s of: %s', function_name, remote_addr, state.request_id)
        remote_url = 'http://{}/request'.format(remote_addr)
        data = {
            'request_id': state.request_id,
            'workflow_name': self.workflow_name,
            'function_name': function_name,
            'no_parent_execution': no_parent_execution,
        }
        response = requests.post(remote_url, json=data)
        response.close()       

     #     for son_next_func in next_next_func: #son_next_func是function_name的子节点的子节点，
        #         state.lock.acquire()
        #         if state.executed[son_next_func] == False:#避免一个节点有多个父节点，所以只需要启动一次
        #             son_next_func_ip = self.func_ip[son_next_func]
        #             state.executed[son_next_func] = True #表示启动了
        #             state.lock.release()
        #             if son_next_func_ip == self.host_addr:
        #                 job = gevent.spawn(self.trigger_function_local_lambda,state,son_next_func,son_next_func_ip,True)
        #             else:
        #                 job = gevent.spawn(self.trigger_function_remote_lambda,state,son_next_func,son_next_func_ip,True)
        #             jobs.append(job)
        #         else:
        #             state.lock.release()
        # if len(jobs) != 0:
        #     gevent.joinall(jobs)

    #todo:一次性修改
    def trigger_function_lambda_next(self,state:WorkflowState,function_name:str)->None:
        #print(' trigger_function_lambda_next, the function_name:',function_name)
        #print(' trigger_function_lambda_next, the function_name:%s',function_name)
        self.states['function_name'] = "done" #表示这个函数已经完成了
        
        func_info = self.get_function_info(function_name) #这个函数的函数信息
        log.info('12trigger_function_lambda_next,function_name:%s and func_info:%s',function_name,func_info)
        print('trigger_function_lambda_next,function_name:',function_name, ' and func_info:',func_info)
        jobs = []
        next_func_list = func_info['next']
        if len(next_func_list) == 0:
            return 
        log.info("13 trigger_function_lambda_next,the next_func_list:%s",next_func_list)

        for next_func in next_func_list:
            next_func_info = self.get_function_info(next_func)
            next_next_func_list = next_func_info['next']
            log.info("13 trigger_function_lambda_next,the next_next_func_list:%s",next_next_func_list)
            for next_next_func in next_next_func_list:
                state.lock.acquire()
                #
                # son_next_func_ip = self.func_ip[son_next_func]
                next_next_func_ip = self.func_ip[next_next_func]
                """
                if next_next_func_ip == self.host_addr:
                    job  = gevent.spawn(self.trigger_function_local_lambda,state,next_next_func,next_next_func_ip,True)
                    jobs.append(job) 
                else:
                    job  = gevent.spawn(self.trigger_function_remote_lambda,state,next_next_func,next_next_func_ip,True)
                    jobs.append(job) 
                """
                if next_next_func not in state.record_funcs:
                    log.info("14 trigger_function_lambda_next,the next_next_func:%s ",next_next_func)
                else:
                    log.info("14.2 trigger_function_lambda_next,the next_next_func:%s and state.record_funcs[%s]:%s",next_next_func,next_next_func,state.record_funcs[next_next_func])

                if next_next_func not in state.record_funcs or  state.record_funcs[next_next_func] == False:#未被启动
                    state.record_funcs[next_next_func] = True
                    state.lock.release()
                    if next_next_func_ip == self.host_addr:
                        job  = gevent.spawn(self.trigger_function_local_lambda,state,next_next_func,next_next_func_ip,True)
                        jobs.append(job)
                    else:
                        job  = gevent.spawn(self.trigger_function_remote_lambda,state,next_next_func,next_next_func_ip,True)
                        jobs.append(job)
                else:
                    state.lock.release()
                
        if len(jobs) != 0:
            gevent.joinall(jobs)
        else:
            return 

        # """ 
        # next_func_list = func_info['next']
        # if len(next_func_list) == 0:
        #     return #这个函数没有后续节点
        # jobs = [] 
        # for next_func in next_func_list:
        #     #某些函数的后续节点函数
        #     self.lock.acquire()
        #     if state.executed[next_func] == False:
        #         state.executed[next_func] = True
        #         next_func_ip = self.func_ip[next_func]
        #         if next_func_ip == self.host_addr:
        #             job = gevent.spawn(self.trigger_function_local_lambda,state,next_func,next_func_ip,True)
        #             jobs.append(job)
        #         else:
        #             job = gevent.spawn(self.trigger_function_remote_lambda,state,next_func,next_func_ip,True)
        #             jobs.append(job)
        #         self.lock.release()
        #     else:
        #         self.lock.release()
        # if len(jobs) != 0:
        #     gevent.joinall(jobs)
        # else:
        #     return 
        # """
        
        # for next_func_name in next_func:#next_func_name是这个函数的子节点，已经被启动了
        #     next_func_info = self.get_function_info(next_func_name)
        #     next_next_func = next_func_info['next']
        #     if len(next_next_func) == 0:
        #         return #没有孙子节点
        #     for son_next_func in next_next_func: #son_next_func是function_name的子节点的子节点，
        #         state.lock.acquire()
        #         if state.executed[son_next_func] == False:#避免一个节点有多个父节点，所以只需要启动一次
        #             son_next_func_ip = self.func_ip[son_next_func]
        #             state.executed[son_next_func] = True #表示启动了
        #             state.lock.release()
        #             if son_next_func_ip == self.host_addr:
        #                 job = gevent.spawn(self.trigger_function_local_lambda,state,son_next_func,son_next_func_ip,True)
        #             else:
        #                 job = gevent.spawn(self.trigger_function_remote_lambda,state,son_next_func,son_next_func_ip,True)
        #             jobs.append(job)
        #         else:
        #             state.lock.release()
        # if len(jobs) != 0:
        #     gevent.joinall(jobs)
        # """


    # trigger a function that runs on local
    def trigger_function_local(self, state: WorkflowState, function_name: str, no_parent_execution = False) -> None:
        log.info('trigger local function: %s of: %s', function_name, state.request_id)
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

    
    def clear_db(self, request_id):
        repo.clear_db(request_id)