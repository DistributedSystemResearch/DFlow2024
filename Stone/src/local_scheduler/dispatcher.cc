#include "dispatcher.h"
#include "function_manager.h"
#include "workersp.h"

#include <chrono>

Dispatcher::Dispatcher(const std::vector<std::string> & workflow_pool) {
    workflow_pool_ = workflow_pool;
    LOG(INFO) <<" Dispatcher::Dispatcher,the workeflow_pool.size():"<<workflow_pool.size();
    for(auto workflow_name: workflow_pool) {
        WorkerSPManager  * wsp =new  WorkerSPManager(host_addr_,workflow_name,min_port_);
        min_port_ += 2000;
        name_workersp_[workflow_name] = wsp;
    }
}


// Dispatcher::Dispatcher(const Dispatcher & dis) {
//     name_workersp_ = dis.name_workersp_;
// }

void Dispatcher::init(const std::string &workflow_name, const Json &js) {
    WorkerSPManager  * wsp = get_workersp(workflow_name);
    wsp->DebugQueue();
    FunctionManager * fun = wsp->getFunctionManager();
    fun->Debug();
    wsp->init(js);//根据收到的json file初始化workflow
    name_workersp_[workflow_name] = wsp;
}

void Dispatcher::trigger_start_function(const std::string & workflow_name , const std::string & request_id ,const std::vector<std::string> & start_functions){
    auto start  = std::chrono::system_clock::now();
    WorkerSPManager  * wsp = get_workersp(workflow_name);
    WorkflowState * state = get_state(workflow_name,request_id);
    FunctionManager * fun = wsp->getFunctionManager();
    fun->Debug();
    wsp->trigger_function(state,start_functions);
    auto end  = std::chrono::system_clock::now();
    auto duration = end - start ;
    double trigger_start_function_time  =     (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000;
    LOG(INFO)<<"Dispatcher::trigger_start_function,the workflow_name:"<<workflow_name <<" and trigger_start_function_time:"<<trigger_start_function_time  <<" second";
    return ;
}

void Dispatcher::trigger_local_remote_function(const std::string &workflow_name, const std::string &request_id, const std::string &func_name) {
    WorkerSPManager  * wsp = get_workersp(workflow_name);
    WorkflowState * state = get_state(workflow_name,request_id);
    LOG(INFO)<<"Dispatcher::trigger_function,the state->request_id:"<< state->get_request_id() ;
    wsp->trigger_local_remote_function(state,func_name,host_addr_);
}