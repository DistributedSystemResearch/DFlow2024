#include "../utils/logging.h"

#include "workersp.h"
#include "wfrest/json.hpp"

#include "../utils/logging.h"
//using namespace wfrest;
using Json = nlohmann::json;

#include <map>
#include <vector>
#include <string> 

class Dispatcher {
    public:
        Dispatcher(const std::vector<std::string> & workflow_pool);//这个构造函数初

        Dispatcher(const Dispatcher & dis) {
            workflow_pool_ = dis.workflow_pool_;
            name_workersp_ = dis.name_workersp_;
            host_addr_ = dis.host_addr_;
            min_port_ = dis.min_port_;
        } 

        Dispatcher & operator=(const Dispatcher & dis){
            //name_workersp_  = dis.name_workersp_;
            workflow_pool_ = dis.workflow_pool_;
            name_workersp_ = dis.name_workersp_;
            host_addr_ = dis.host_addr_;
            min_port_ = dis.min_port_;
            return *this;
        }

        void init(const std::string & workflow_name,const Json & js );

        WorkerSPManager  * get_workersp(const std::string  & workflow_name) {
            return name_workersp_[workflow_name];
        }

        WorkflowState  * get_state(const std::string &  workflow_name, const  std::string & request_id) {
            WorkerSPManager * wsp = get_workersp(workflow_name);
            return wsp->get_state(request_id);
        }

        void del_state(const std::string & workflow_name, const std::string & request_id,bool master) {
             WorkerSPManager * wsp = get_workersp(workflow_name);
             return wsp->del_state(request_id,master);
        }

        void trigger_start_function(const std::string & workflow_name , const std::string & request_id ,const std::vector<std::string> & start_functions) ;
            //这个start_function是表示在这台机器上运行的start functions 

        void trigger_local_remote_function(const std::string & workflow_name , const std::string & request_id ,const std::string & func_name) ;
        //处理别的机器post过来的函数
        ~Dispatcher() {
            std::map<std::string , WorkerSPManager *>::iterator  iter = name_workersp_.begin();
            while(iter != name_workersp_.end()) {
                delete iter->second;
            }

        }


    private:
        std::vector<std::string> workflow_pool_;
        std::map<std::string,WorkerSPManager *> name_workersp_;

        uint64_t min_port_ = 10000;
        std::string host_addr_ = "172.16.187.15:8000";//自己设置


};