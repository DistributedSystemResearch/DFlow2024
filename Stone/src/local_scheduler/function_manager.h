#ifndef FUNCTION_MANAGER_H
#define FUNCTION_MANAGER_H

#include <cpr/response.h>
#include <queue>
#include <map>
#include <string> 
#include <cstdlib>
#include <mutex>

#include <cpr/cpr.h>

#include "wfrest/json.hpp"

#include  "../utils/logging.h"

using Json = nlohmann::json;

class FunctionManager {
    public:

        FunctionManager(const std::string & workflow_name, const std::string  & workflow_image_name, const int &  min_port)
            :workflow_name_(workflow_name)
            ,workflow_image_name_(workflow_image_name)
            ,min_port_(min_port) {
               // workflow_functions_ = functions;
                int max_port = min_port + 4999;

                for(int port = min_port;  port < max_port; port++) {
                    port_queue_.push(port);//这个表示该workflow可以使用的端口数
                }
                LOG(INFO)<<"1 Function::FunctionManager,the min_port:"<<min_port <<" and max_port:"<<max_port ;
                LOG(INFO)<<"2 the FunctionManager::FunctionManager,port_queue.size()"<<port_queue_.size() << " and min_port" << min_port  ;
                init();//清除容器
            }

        void set_function(const std::vector<std::string> & functions) {
            workflow_functions_ = functions;//设置这个FunctionManager的函数
            auto func_size = workflow_functions_.size();
            auto i =0;
        }

        ~FunctionManager() {
            workflow_functions_.clear();
            std::map<std::string,std::queue<int>>::iterator iter;
            while(iter != container_pool_.end()) {
                std::queue<int>  q = iter->second;
                while(q.empty() == false) {
                    q.pop();
                }
            }
            container_pool_.clear();
        }

            FunctionManager() = default;//默认构造函数

            FunctionManager(const FunctionManager & rhs) {
                workflow_name_ = rhs.workflow_name_;
                workflow_image_name_ = rhs.workflow_image_name_;
                min_port_ = rhs.min_port_;
                workflow_functions_ = rhs.workflow_functions_;
            }

            FunctionManager & operator=(const FunctionManager & rhs) {
                workflow_name_ = rhs.workflow_name_;
                workflow_image_name_ = rhs.workflow_image_name_;
                min_port_ = rhs.min_port_;
                workflow_functions_ = rhs.workflow_functions_;
                return * this;
            }

            void set(const  std::string &workflow_name, const std::string &workflow_image_name, const int & min_port);

            int  getPort() ;

            void putPort(int port);

            void runContainer(int port);//用std::system 运行容器 

            size_t size() {
                return port_queue_.size();
            }

            void Debug() {
                LOG(INFO)<<"functionmanager,the workflow_name:"<< workflow_name_ ;
            }

        void init() {
            LOG(INFO) <<"clearing previous containers";
            std::string command = "docker rm -f $(docker ps -aq --filter label=workflow)";
            std::system(command.c_str());//清除容器
        }

        /*
                self.function_manager.run_lambda(info['function_name'], state.request_id,
                             info['runtime'], info['my_input'], info['my_output'],
                             info['to'], {},func_ip,self.workflow_name) #TODO(error) 
        */

        void run_function(const std::string & func_name, const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output);
        //run_function的设计思路:1)运行一个容器，这个可以看contaier_pool_,
        //std::queue<int> q = container_pool_[func_name]
        //if q.empty()  == false,则取出一个端口，然后向这个端口发一个json,用cpr 
        //if q.empty() == true,表示没有容器可供复用了，1)获取一个端口 2)根据这个端口则std::system run一个container,
        //然后向这个端口发json  file
        //收到回复后，将这个端口返回到q中,使用container_pool_mutex_来更新
        //UPDATE记住:给端口发json文件，是一个同步操作，也就是必须等docker的回复，才能进行下一步操作

        void start_container(int port ,const std::string  & func_image_name) ;//根据这个port run一个docker
        
        Json getJson(const std::string &  func_name,const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output) ;

        cpr::Response  post_request(const Json & js, int port , const std::string & remote_url);

        std::string geturl(const int & port, const std::string & status );

        Json getInitJson(const std::string &func_name);

        void container_init_and_run(const std::string &  func_name,const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output, const int  & port );

        void container_run(const std::string &  func_name,const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output, const int  & port );
        //容器复用
    private:
        std::string workflow_name_;
        std::string workflow_image_name_;
        //std::vector<std::mutex> func_mutex_;//
        std::mutex container_pool_mutex_;//用来更新container_pool
        //std::map<std::string,int> func_number_;//key是函数名，value是第几个函数
       // std::map<std::string,std::mutex> func_name_mutex_;//每个函数名一个细粒度锁
        std::map<std::string,std::queue<int>>  container_pool_;//key是image_name,类型为str,如wc_image,wc_start
        //value是端口,维持着端口的队列，便于容器复用
        int min_port_;//这个workflow_name可用的容器端口范围
        std::queue<int> port_queue_;
        std::mutex image_queue_mutex_;
        std::vector<std::string> workflow_functions_;//这个workflow的所有function
};

#endif 