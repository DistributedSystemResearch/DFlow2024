### proxy.py给C++ server发送的json数据 

"""
data = {
        'request_id': request_id,
        'workflow_name': workflow_name,
        'function_name': function_name,
        'no_parent_execution': True
}
"""

data = {} 
data['request_id'] = request_id 
data['workflow_name'] = workflow_name 
data['function_name'] = function_name 
#需要记录这个function_name的子节点
#记录这个functon的functionip


#第一个设计
#在workersp.py这里用到了self.function_info\
#所以func_info = self.get_function_info(function_name) 
#对于这个func_info,1)得到函数的运行机器的ip 2)
##TODO 
data['ips'] ={
    function_name: "127.0.0.1:8000", #ip，到时候要更改,

    #son_function是表示它的子函数集合，
    #我们需要知道其ip
    'son_function': [{x:"xxxxx"},{y:"xxxxx"} ]
    #TODO:这个x是表示子函数名，xxxx是表示其ip,x在y前面，因为x的父节点做少，所以排在前面
} 
#TODO:这个可以通过读info_ip_db这里找到
###TODO:或者，我在grouping.py和parse.py这里可以做好

#得到一个workflow所有的函数名字的:funcs =  repo.get_function_ip(self.info_ip_db,workflow_name)
data[workflow_name + "funcs"] =  repo.get_function_ip(self.info_ip_db,workflow_name) #一个workflow中所有函数的集合
data[workflow_name + 'ips'] = {} #记录函数的ip,key是函数名，value是ip


self.info_db = workflow_name + '_function_info' 
funcs =  repo.get_function_ip(self.info_ip_db,workflow_name)  #得到一个workflow所有的函数名字的

#data[workflow_name +"next"] = {} #记录函数的next 
#一个数据结构，key是函数名，value是一个list,这个list表示它的子节点函数
#计算func的next 

#第2个设计，触发子函数,需要知道子函数的ip,
#我们的设计中，最好做一个排序，对于有子节点的函数，其子节点的父节点最少的排前面


