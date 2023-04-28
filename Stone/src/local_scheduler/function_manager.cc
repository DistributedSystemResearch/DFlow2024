#include "function_manager.h"



#include <cpr/body.h>
#include <cpr/cprtypes.h>
#include <cpr/low_speed.h>
#include <cpr/response.h>
#include <queue>
#include <stdexcept>
#include <chrono> 

#include <sys/types.h>
#include <unistd.h>
#include <sys/syscall.h>
#define gettid() syscall(__NR_gettid)

void FunctionManager::set(const std::string &workflow_name, const std::string &workflow_image_name, const int &min_port) {
    workflow_name_ = workflow_name;
    workflow_image_name_ = workflow_image_name;
    /*int max_port = min_port + 4999;

    for(int port = min_port;  port < max_port; port++) {
        port_queue_.push(port);//这个表示该workflow可以使用的端口数
    }*/
    LOG(INFO)<<"the FunctionManager::set,port_queue.size()"<<port_queue_.size() << " workflow_name:"<<workflow_name_ <<" workflow_image_name:"<<workflow_image_name_ ;
}

int FunctionManager::getPort() {
    if(port_queue_.empty()) {
        //端口用完了，异常产生
        std::string error_message = "no idle port , and workflow_name:" + workflow_name_;
        throw std::runtime_error(error_message);
    }

    int port =  port_queue_.front();
    port_queue_.pop();//出队
    return port ;
}

void FunctionManager::putPort(int port ) {
    //剩余的端口放回队列
    port_queue_.push(port);
    return ;
}


void FunctionManager::run_function(const std::string & func_name, const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output) {
    //if(container_pool_.count)
    std::string func_image_name = workflow_image_name_ + func_name;
    container_pool_mutex_.lock();
    LOG(INFO)<<"1 FunctionManager::run_function,the func_image_name:"<<func_image_name ;
    if(container_pool_.count(func_image_name) == 0) {
        //这个func_image_name第一次出现
        std::queue<int > q;
        container_pool_[func_image_name] = q;
        int port = getPort();
        LOG(INFO) << "2 FunctionManager::run_function,the workflow_name:"<<workflow_name_ <<" and func_name:"<<func_name <<" get the port:" << port;
        container_pool_mutex_.unlock();
        auto start = std::chrono::system_clock::now();
        start_container(port, func_image_name);//TODO 运行了容器,这里或许需要update 
        auto end = std::chrono::system_clock::now();
        auto duration = end - start ;
        double start_container_time  =  (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den) / 1000;
        LOG(INFO)<<"3 Function::run_function,the function_name:"<<func_name <<" and start container time:"<<start_container_time <<" second" ;
        //run container了，就先get status,然后post init,然后post run 

        start = std::chrono::system_clock::now();
        container_init_and_run(func_name, request_id,runtime, input, output, port);
        end  = std::chrono::system_clock::now();
        duration = end - start ;
        double container_init_run_time  =  (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den) / 1000 ;
        LOG(INFO)<<"4 Function::run_function, the function_name:"<<func_name <<" and container_init_run_time:"<<container_init_run_time <<" second";
       
        container_pool_mutex_.lock();
        std::queue<int> q1 = container_pool_[func_image_name];
        q1.push(port);
        container_pool_[func_image_name] = q1;
        container_pool_mutex_.unlock();
        return ;
    } else {
        //不是第一次出现，这就涉及到两者情况
        //1)对应的队列没有port了，即此时需要申请port,然后运行
        //2)对应的队列还有port,从对头那就行，用完后，返回队尾
        std::queue<int> q = container_pool_[func_image_name];
        if(q.empty()) {
            int port  = getPort();
            container_pool_mutex_.unlock();
            auto start = std::chrono::system_clock::now();
            start_container(port, func_image_name);//TODO 运行了容器,这里或许需要update          
            auto end = std::chrono::system_clock::now();
            auto duration = end - start ;
            double start_container_time  =  (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000;
            LOG(INFO)<<"5 Function::run_function,the function_name:"<<func_name <<" and start container time:"<<start_container_time  <<" second";
            LOG(INFO) << "6  FunctionManager::run_function,the workflow_name:"<<workflow_name_ <<" and func_name:"<<func_name <<" get the port:" << port;
           
            start = std::chrono::system_clock::now();
            container_init_and_run(func_name, request_id,runtime, input, output, port);
            end  = std::chrono::system_clock::now();
            duration = end - start;
            duration = end - start ;
            double container_init_run_time  =  (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000;
            LOG(INFO)<<"7 Function::run_function, the function_name:"<<func_name <<" and container_init_run_time:"<<container_init_run_time <<" second";

            container_pool_mutex_.lock();
            std::queue<int> q1 = container_pool_[func_image_name];
            q1.push(port);
            container_pool_[func_image_name] = q1;
            container_pool_mutex_.unlock();
            return ;
        } else {
            int port  = q.front();
            q.pop();
            //容器复用
            LOG(INFO) << "8 FunctionManager::run_function,the workflow_name:"<<workflow_name_ <<" and func_name:"<<func_name <<" get the port:" << port;
            container_pool_mutex_.unlock();

            auto start = std::chrono::system_clock::now();
            container_run(func_name, request_id,runtime, input, output, port);//只需要发送请求给容器就行
            auto end = std::chrono::system_clock::now();
            auto duration = end - start ;
            double container_init_run_time  =  (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) /1000 ;
            LOG(INFO)<<"9 Function::run_function, the function_name:"<<func_name <<" and container_init_run_time:"<<container_init_run_time <<" second";
            container_pool_mutex_.lock();
            std::queue<int> q1 = container_pool_[func_image_name];
            q1.push(port);
            container_pool_[func_image_name] = q1;
            container_pool_mutex_.unlock();
            return ;
        }
    }
}


void FunctionManager::start_container(int port, const std::string & func_image_name) {
    std::string command = "docker run -itd  -p ";
    
    std::string port_map= std::to_string(port) +":5000"  ;//映射到docker的5000端口,增加label 
    std::string label  = "  -l workflow  ";
    command = command + port_map +    label + func_image_name;
    std::system((std::move(command).c_str()));//运行一个容器

    //docker run -itd -p 25000:5000 -l workflow epigenomics_fastqsplit_00000001
}

Json FunctionManager::getJson(const std::string &func_name, const std::string &request_id, float runtime, const std::vector<std::string> &input, const std::map<std::string,int> &output) {
    Json js;
    js["request_id"] = request_id;
    js["function_name"] = func_name;
    js["workflow_name"] = workflow_name_;
    js["ip"] = "127.0.0.1";
    js["to"] = "to";
    js["runtime"] = runtime;
    auto input_result = Json::array();
    for(auto func_input : input) {
        input_result.push_back(func_input);
    }
    js["input"] = input_result;
    
  //  auto output_result = Json::array();
    // for(auto func_output: output) {
    //     output_result.push_back(func_output);
    // }
    js["output"] = output;//TODO:这里或许需要修改
    LOG(INFO) <<"10 Function::getJson,the function_name:" << func_name <<" and workflow_name:" << workflow_name_ <<" and request_id:"<<request_id << " and js.dump" << js.dump();

    return js ;
}

std::string FunctionManager::geturl(const int &port , const std::string & flag) {
    std::string host_url = "http://127.0.0.1:";
    std::string remote_url = host_url + std::to_string(port)  + "/"  + flag;
    return remote_url ;
}

cpr::Response FunctionManager::post_request(const Json &js, int port,const std::string & remote_url) {

    LOG(INFO)<<"11 FunctionManager::post_request remote_url:"<<remote_url << " and js.dump:"<< js.dump()  ; 

    cpr::Response r = cpr::Post(cpr::Url{remote_url}, cpr::Body{js.dump()},cpr::Header{{"Content-Type", "application/json"}});
    LOG(INFO) <<"12 FunctionManager::post_request,the r.status.code " << r.status_code  <<" and remote_url:"<<remote_url;
    return r ;
}

Json FunctionManager::getInitJson(const std::string &func_name ) {
    Json js;
    js["workflow"] = workflow_name_;
    js["function"] = func_name;
    return js ;
}

void FunctionManager::container_init_and_run(const std::string &  func_name,const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output, const int & port ){
    //先status,然后初始化得到init json,给http://127
    std::string status = "status";
    LOG(INFO) <<"13 FunctionManager::container_init_and_run,func_name:"<< func_name << " and workflow_name:"<<workflow_name_ <<" and request_id:"<<request_id <<" and port:"<<port <<" threadid:"<<gettid(); 
    std::string status_url = geturl(port,status);
    LOG(INFO)<<"14 FunctionManager::container_init_and_run,the status_url:"<<status_url <<" and port:"<< port  <<" and threadid:"<< gettid() << " function_name:"<<func_name <<" and request_id:"<<request_id;

    auto start  = std::chrono::system_clock::now();
    while(1){
        cpr::Response r = cpr::Get(cpr::Url{status_url});
        if(r.status_code == 200) {
            LOG(INFO)<<"15 FunctionManager::container_init_and_run,the r.status_code:"<<r.status_code << " function_name:"<<func_name <<" and request_id:"<<request_id;;
            break;
        } 
    }
    auto end = std::chrono::system_clock::now();
    auto duration = end - start ;
    double status_time =    ( double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000;
    LOG(INFO)<<"16 Function::container::init_and_run,the function_name:"<<func_name<<" and its status time:"<<status_time << " and runtime:"<<runtime <<" second"; 

    start = std::chrono::system_clock::now();
    std::string initFlag = "init";
    std::string init_url = geturl(port,initFlag);
    LOG(INFO)<<"17 FunctionManager::container_init_and_run,the init_url:"<<init_url <<" and port:"<< port  <<" and threadid:"<< gettid() << " function_name:"<<func_name <<" and request_id:"<<request_id;;
    Json init_js = getInitJson(func_name);
    auto init_resp = post_request(init_js,port,init_url);
    end = std::chrono::system_clock::now();
    duration = end - start;
    double init_time = (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000;
    LOG(INFO)<<"18 Function::container::init_and_run,the function_name:"<<func_name<<" and its init time:"<<init_time << " and runtime:"<<runtime<<" second"; 
    DCHECK(init_resp.status_code == 200);

    std::string run = "run";
    start = std::chrono::system_clock::now();
    std::string run_url = geturl(port,run);
    LOG(INFO)<<"19 FunctionManager::container_init_and_run,the run_url:"<<run_url <<" and port:"<< port  <<" and threadid:"<< gettid() << " function_name:"<<func_name <<" and request_id:"<<request_id;;
    Json run_js = getJson(func_name,request_id,runtime,input,output);
    auto run_resp = post_request(run_js,port,run_url);
    end = std::chrono::system_clock::now();
    duration = end - start;
    double docker_run_time = (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000 ;
    LOG(INFO)<<"20 Function::container_init_and_run,the function_name:"<<func_name<<" and its docker_run_time:"<<docker_run_time << " and runtime:"<<runtime << " second"; 

    LOG(INFO) <<"21 FunctionManager::container_init_and_run,the run_resp.status.code:" << run_resp.status_code  <<" and run_utl:"<< run_url<< " function_name:"<<func_name <<" and request_id:"<<request_id;;
    return ;
}   


void FunctionManager::container_run(const std::string &  func_name,const std::string & request_id, float runtime, const std::vector<std::string> & input, const std::map<std::string,int> & output, const int & port ){
    //容器复用的函数，只需要想http://127.0.0.1:port/run发送json文件就OK了
    std::string run = "run";
    auto start = std::chrono::system_clock::now();
    std::string run_url = geturl(port,run);
    LOG(INFO)<<"22 FunctionManager::container_run,the run_url:"<<run_url <<" and port:"<< port  <<" and threadid:"<< gettid() << " function_name:"<<func_name <<" and request_id:"<<request_id;;
    Json run_js = getJson(func_name,request_id,runtime,input,output);
    auto run_resp = post_request(run_js,port,run_url);
    auto end = std::chrono::system_clock::now();
    auto duration = end - start;
    double docker_run_time =  (double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ) / 1000 ;
    LOG(INFO)<<"23 Function::container_run,the function_name:"<<func_name<<" and its docker_run_time:"<<docker_run_time << " and run_time:"<<runtime <<" second"; 
    LOG(INFO) <<"24 FunctionManager::container_init_and_run,the run_resp.status.code:" << run_resp.status_code  <<" and run_utl:"<< run_url<< " function_name:"<<func_name <<" and request_id:"<<request_id;;
    return ;
}   