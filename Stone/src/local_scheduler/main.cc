#include "workflow/WFFacilities.h"
#include <csignal>
#include "wfrest/HttpServer.h"
#include "wfrest/json.hpp"
#include <string> 
#include <vector>
#include <iostream>
#include "../utils/logging.h"
#include<typeinfo>
#include <string>
#include "dispatcher.h"
#include <cstdlib>

using namespace wfrest;
using Json = nlohmann::json;

static WFFacilities::WaitGroup wait_group(1);

void sig_handler(int signo){
    wait_group.done();
}

    std::vector<std::string> workflow_pool  ={"cycles","epigenomics","genome","soykb","fileprocessing","wordcount"};
 
 
    Dispatcher * dispatcher =new  Dispatcher(workflow_pool);

int main() {
    

    signal(SIGINT, sig_handler);

    HttpServer svr;

    svr.POST("/clear",[](const HttpReq *req, HttpResp *resp){
        //TODO update 清除state
        if (req->content_type() != APPLICATION_JSON){
            resp->String("NOT APPLICATION_JSON");
            return;
        }
        Json js = std::move(req->json());
        LOG(INFO)<<"POST clear,the json:"<<js.dump();
        std::string workflow_name = js.at("workflow_name");
        std::string request_id = js.at("request_id");
        bool master = js.at("master");
        dispatcher->del_state(workflow_name, request_id,master);
    });

    svr.POST("/clear_container",[](const HttpReq *req, HttpResp *resp) {
        LOG(INFO) <<" clearing containers";
        std::string command = "docker rm -f $(docker ps -aq --filter label=workflow)";
        std::system(command.c_str());
    });

    svr.POST("/request",[](const HttpReq *req, HttpResp *resp){ 
        if (req->content_type() != APPLICATION_JSON){
            resp->String("NOT APPLICATION_JSON");
            return;
        }
        Json js = req->json();
        //LOG(INFO)<<"svr.POST(request):the js:"<<js.dump();
        std::string workflow_name = js.at("workflow_name");
        std::string request_id = js.at("request_id");
        std::string function_name = js.at("function_name");
        //TODO 
        LOG(INFO) <<" svr.POST(request),the workflow_name:"<< workflow_name <<" and function_name:"<<function_name <<" and request_id:"<<request_id;
        dispatcher->trigger_local_remote_function(workflow_name,request_id,function_name);
    });

    //启动start functions
    svr.POST("/start",[](const HttpReq *req, HttpResp *resp){
        //TODO update 
        if (req->content_type() != APPLICATION_JSON){
            resp->String("NOT APPLICATION_JSON");
            return;
        }

        Json js = std::move(req->json());
        std::string workflow_name = js.at("workflow_name");
        std::string request_id = js.at("request_id");
        LOG(INFO) <<" \n\n---------------main start---------------\n\n";
        LOG(INFO) <<" the workflow_name:"<<workflow_name <<" and request_id:"<<request_id ;
        std::string start_workflow_name = workflow_name + "_start";
        auto funcs = js.at(start_workflow_name);
        std::vector<std::string> start_funcs;
        if(funcs.is_array()) {
            auto start_size = funcs.size();
            start_funcs.resize(start_size);
            for(auto i= 0; i < start_size; i++) {
              //  LOG(INFO)<<"the workflow_name:"<< workflow_name <<" and start_function size:"<<start_size <<" and i:"<<i <<" func_name:"<<funcs[i];
                start_funcs[i] = funcs[i];
            }
        }

        dispatcher->trigger_start_function(workflow_name,request_id,start_funcs);
    });


    svr.POST("/init", [](const HttpReq *req, HttpResp *resp){
        if (req->content_type() != APPLICATION_JSON){
            resp->String("NOT APPLICATION_JSON");
            return;
        }
        //Json js = req->json();
        //if(js.at("try").is_string()){
           // std::string s = js["try"];
           // std::cout<<"s:"<<s<<std::endl;
      //  }
      Json js = std::move(req->json());//we get the json
      
      std::string workflow_name = js.at("workflow_name");//得到workflow_name 
      LOG(INFO)<<"POST,init ,the workflow_name:"<<workflow_name ;
      dispatcher->init(workflow_name,js);
    });
    /*svr.POST("/request", [](const HttpReq *req, HttpResp *resp){
        //TODO ,这个处理master机器触发的请求
    });*/
    svr.POST("/test", [](const HttpReq *req, HttpResp *resp){
        Json js = req->json();
        LOG(INFO) <<" the js.dump():"<<js.dump() ;
    });

    svr.POST("/rerun", [](const HttpReq *req, HttpResp *resp){
        Json js = req->json();
        LOG(INFO) <<" the js.dump():"<<js.dump() ;
        std::system("bash run.sh");
    });

    std::string ip ="172.16.187.15";//本机ip,可以更新

    if (svr.start(ip.c_str(), 8000) == 0){
        std::cout<<"listen on 8000" <<  std::endl;
        LOG(INFO)<<"listen on  "<< ip<<":" <<  8000 ;
        wait_group.wait();
        svr.stop();
    } else{
        fprintf(stderr, "Cannot start server");
        exit(1);
    }
    return 0;
}