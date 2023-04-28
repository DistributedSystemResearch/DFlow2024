#ifndef WORKERSP_H
#define  WORKERSP_H 

#include <string>
#include <map> 
#include <vector>
#include <thread>
#include <mutex>
#include <chrono> 

#include <cpr/cpr.h>

#include "wfrest/json.hpp"
#include "function_manager.h"
#include "../utils/logging.h"
//using namespace wfrest;
using Json = nlohmann::json;

class FunctionManager;

class WorkflowState {
    public:
        WorkflowState( const std::string & request_id,const std::vector<std::string>  & all_funcs):request_id_(request_id) {
            for(auto funcs:all_funcs) {
                executed_[funcs] = false;
                record_funcs_[funcs] = false;
            }
        }
        WorkflowState(){
            request_id_ = "";
        } //默认构造函数
        WorkflowState(const WorkflowState &state) {
            request_id_ = state.get_request_id();
            executed_ = state.executed_;
            record_funcs_ = state.record_funcs_;
        };

        WorkflowState & operator=(const WorkflowState & state) {
            request_id_ = state.get_request_id();
            executed_ = state.executed_;
            record_funcs_ = state.record_funcs_;
            return *this;
        };

        //WorkflowState(const WorkflowState & state) = default;
        void set_request_id(const std::string  & request_id){
            request_id_ = request_id;
        }
        void set_all_funcs(const std::vector<std::string> & all_funcs) {
            state_lock_.lock();
            for(auto funcs:all_funcs) {
                executed_[funcs] = false;
                record_funcs_[funcs] = false;
                remote_funcs_[funcs] = false;
            }
            state_lock_.unlock();
        }
        std::string get_request_id() const {
            return  request_id_;
        }
        std::map<std::string,bool> get_executed()   {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);

            return executed_;
        }

        std::map<std::string,bool> get_record_funcs(){
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            return record_funcs_;
        }

        bool get_funcs_executed_state(const std::string & func_name) {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            return executed_[func_name];
        }

        bool get_record_fucns_state(const std::string & func_name) {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            return record_funcs_[func_name];
        }

        void set_funcs_executed_state(const std::string &func_name) {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            executed_[func_name] = true;

        }

        void set_funcs_record_state(const std::string & func_name) {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            record_funcs_[func_name] = true;
        }

        void set_funcs_remote_state(const std::string & func_name) {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            remote_funcs_[func_name] =  true;
        }

        bool get_funcs_remote_state(const std::string & func_name) {
            std::lock_guard<std::mutex> lock_guard(state_lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            return remote_funcs_[func_name];
        }
        ~WorkflowState() {
            executed_.clear();
            record_funcs_.clear();
            remote_funcs_.clear();
            
        }

        void acquire() {
            state_lock_.lock();
        }

        void release() {
            state_lock_.unlock();
        }

    private:
        std::string request_id_;
        std::map<std::string,bool> executed_;
        std::map<std::string,bool> record_funcs_;
        std::map<std::string, bool> remote_funcs_;//记录remote function只能启动一次
        std::mutex state_lock_;

};

class WorkerSPManager {
    public:
        WorkerSPManager(const std::string & host_addr , const std::string & workflow_name):host_addr_(host_addr),workflow_name_(workflow_name) {

        }

        WorkerSPManager(const std::string & host_addr , const std::string & workflow_name,const uint64_t & min_port)
        :host_addr_(host_addr)
        ,workflow_name_(workflow_name)
        ,min_port_(min_port) {
            //workflow_image_[""]
            LOG(INFO)<<"WorkerSPManager::WorkerSPManager,the workflow_name:"<<workflow_name <<" and min_port:"<<min_port <<" and host_addr:"<<host_addr;
            std::string wc_name = "wordcount";
            std::string wc_image="wc_";
            workflow_image_[wc_name] = wc_image;

            std::string fp_name = "fileprocessing";
            std::string fp_image = "fileprocessing_";
            workflow_image_[fp_name] = fp_image;

            std::string cycles_name ="cycles";
            std::string cycles_image = "cycles_";   
            workflow_image_[cycles_name] = cycles_image;

            std::string epi_name = "epigenomics";
            std::string epi_image = "epigenomics_";
            workflow_image_[epi_name] = epi_image;

            std::string genome_name ="genome";
            std::string genome_image = "genome_";
            workflow_image_[genome_name] = genome_image;

            std::string soykb_name = "soykb";
            std::string soykb_image = "soykb_";
            workflow_image_[soykb_name] = soykb_image;
            
            std::string workflow_image_name = workflow_image_[workflow_name];
            function_manager_ =new   FunctionManager(workflow_name,workflow_image_name,min_port);
            LOG(INFO)<<"WorkerSPManager::WorkerSPManager(const std::string & host_addr , const std::string & workflow_name,const uint64_t & min_port)";
            //function_manager_->set(workflow_name,workflow_image_name,min_port);

            DebugQueue();
        }

        void DebugQueue() {
            LOG(INFO) << " the function.manager.size():"<<function_manager_->size();
        }

        FunctionManager * getFunctionManager() {
            return function_manager_;
        }
        void set(const std::string & host_addr , const std::string & workflow_name,const uint64_t & min_port);

        void init(const Json & js);//收到json文件后初始化

        WorkerSPManager() {
            //state_ = new WorkflowState();
            LOG(INFO)<<"WorkerSPManager::WorkerSPManager";
          //  function_manager_ = new FunctionManager() ;
        };

        WorkerSPManager(const std::string  & host_addr,const std::string &  workflow_name,const Json  & js):host_addr_(host_addr),workflow_name_(workflow_name_) {
            //TODO:根据收到json file初始化
        }
        
        WorkerSPManager & operator=(const WorkerSPManager & wsp){
               all_funcs_ = wsp.all_funcs_;
               all_ips_ = wsp.all_ips_; 
               workflow_name_ = wsp.workflow_name_;
               func_ip_ = wsp.func_ip_;
            //   state_ = wsp.state_;
               host_addr_ = wsp.host_addr_;
               parent_cnt_ = wsp.parent_cnt_;
               funcs_next_ = wsp.funcs_next_;
               funcs_input_ = wsp.funcs_input_;
               funcs_output_ = wsp.funcs_output_;
               funcs_runtime_ = wsp.funcs_runtime_;
               workflow_image_ = wsp.workflow_image_;
               return *this;
        }

        WorkerSPManager(const WorkerSPManager & wsp) {
               all_funcs_ = wsp.all_funcs_;
               all_ips_ = wsp.all_ips_; 
               workflow_name_ = wsp.workflow_name_;
               func_ip_ = wsp.func_ip_;
               //state_ = wsp.state_;
               host_addr_ = wsp.host_addr_;
               parent_cnt_ = wsp.parent_cnt_;
               funcs_next_ = wsp.funcs_next_;
               funcs_input_ = wsp.funcs_input_;
               funcs_output_ = wsp.funcs_output_;
               funcs_runtime_ = wsp.funcs_runtime_;
               workflow_image_ = wsp.workflow_image_;
        } 

        WorkflowState  * get_state(const  std::string &  request_id){
            std::lock_guard<std::mutex> lock_guard(lock_);  //std::lock_guard<std::mutex> lock_guard(local_store_mutex_);
            if(state_.count(request_id) == 0 ) {
                //第一次遇见这个request_id 
                WorkflowState  * state = new WorkflowState();
                //state.request_id_ = request_id;
                state->set_request_id(request_id);
                state->set_all_funcs(all_funcs_);
                state_[request_id] = state;
                LOG(INFO)<<"WorkerSPManager::get_state:"<< state->get_request_id() ;
                return state; //todo 
            }
            WorkflowState * state = state_[request_id];//todo,要修正
            //return state_[request_id];
            return  state;
        }

        ~WorkerSPManager() {
            workflow_image_.clear();
            delete function_manager_;
            std::map<std::string,WorkflowState*>::iterator iter;
            while(iter != state_.end()) {
                delete iter->second;
            }

        }

        void del_state_remote(const std::string  & request_id,  const std::string &  remote_addr) {
            //todo 
            std::string remote_url = "http://" + remote_addr +"/clear";
            Json js ;
            LOG(INFO)<<"del_state_remote,the remote_url:"<<remote_url ;
            js["workflow_name"] = workflow_name_;
            js["request_id"] = request_id;
            js["master"] = false;
            auto r = cpr::Post(cpr::Url{remote_url},cpr::Body{std::move(js.dump())},cpr::Header{{"Content-Type", "application/json"}});

            LOG(INFO) << "Status code:"<<r.status_code ;
        }
        void del_state(const std::string &  request_id, bool master ) {
            LOG(INFO) <<"delete state of " << request_id ;
            lock_.lock();
            if(state_.count(request_id) != 0) {
                state_.erase(request_id);
            }
            lock_.unlock();
            std::vector<std::thread> jobs;
            if(master){
                for(auto ips: all_ips_) {
                    LOG(INFO)<<"the host_addr_:"<<host_addr_ <<" and ips:"<<ips ;
                    if(ips != host_addr_) {
                    //std::thread t(&WorkerSPManager::del_state_remote,this,request_id, ips);
                    
                //    LOG(INFO)<<"the ips:"<< ips ;
                        jobs.push_back(std::thread(&WorkerSPManager::del_state_remote,this,request_id, ips));
                    }
                }
            }
            auto size = jobs.size();
            for(auto i = 0; i < size ; i++) {
                jobs[i].join();
            }
            //jobs.clear();
        }

        void trigger_function(WorkflowState * state, const std::vector<std::string> & start_functions ) ;//todo 

        void trigger_remote_function(WorkflowState * state,const std::string & function_name,const std::string & func_ip);

        void trigger_local_function(WorkflowState  * state,const std::string &  function_name,const std::string & func_ip);

        void trigger_local_remote_function(WorkflowState  * state,const std::string &  function_name,const std::string & func_ip);

        void run_function(WorkflowState * state,const std::string & function_name, const  std::string & func_ip);

        //为了调试
        void PrintVector(const std::string & tag ,const std::string & func_name, const std::vector<std::string>  & v) {
            LOG(INFO) <<"In PrintVector,  **********tag: "  << tag << " the func_name:"<< func_name ;

            /*for(auto i : v) {
                std::cout<<"func_name:"<< " and  its " << tag << " is " << i << std::endl;
            }*/
            if(v.empty()) {
                return ;
            }
            size_t size = v.size();
            for(int i = 0; i < size;i++) {
                std::string temp = v[i];
                LOG(INFO)<<"func_name:"<< func_name <<   " and  its " << tag << " is " << i ;

            }
        }

    private:
        std::vector<std::string> all_funcs_;//某个workflow的所有函数名
        std::vector<std::string> all_ips_;//集群中所有ip
        std::string workflow_name_;//workflow的名字
        std::map<std::string,std::string> func_ip_;//key是函数名，value是ip
        std::map<std::string, WorkflowState * >  state_;
        std::string host_addr_;//自己机器的ip ,这块或许可以用hoplite的试试
        std::map<std::string,int> parent_cnt_;//key是函数名，value是表示节点父节点个数
        std::map<std::string,std::vector<std::string>> funcs_next_;
        //记录函数的next节点,key是函数名，value是一个vector,vector的每一个成员变量是函数名
        std::map<std::string,std::vector<std::string>> funcs_input_;
        //记录函数的输入， key是函数名，value是一个vector,vector的每一个成员变量表示输入的名字，类型为str
        //std::map<std::string,std::vector<std::string>> funcs_output_;
        std::map<std::string,std::map<std::string,int> > funcs_output_;
        //记录函数的输出， key是函数名，value是一个dict,dict中的key是函数的某个输出，value是size
        std::map<std::string,float> funcs_runtime_;
        //记录函数的runtime,key是函数名，value是一个double 
        std::mutex lock_;
        uint64_t min_port_;
        std::map<std::string,std::string> workflow_image_;
        std::mutex state_executd_mutex_;
        std::mutex state_record_mutex_;
        std::mutex state_remote_mutex_;
        FunctionManager * function_manager_;

};

#endif 