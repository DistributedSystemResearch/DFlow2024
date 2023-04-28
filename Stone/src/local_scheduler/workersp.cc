#include <chrono>
#include <thread>
#include <string>

#include "../utils/logging.h"
#include "workersp.h"

void WorkerSPManager::init(const Json &js) {

      LOG(INFO)<<"WorkerSPManager::init,the workflow_name:"<<workflow_name_;
      std::string workflow_all_funcs_name =  workflow_name_ + "_all_funcs";
      auto all_funcs = js.at(workflow_all_funcs_name);//得到worklow的所有函数名,all_funcs是一个python的lisy 
      size_t all_funcs_size  = all_funcs.size();

      std::string workflow_all_funcs_ip = workflow_name_ + "_ips";
      auto all_funcs_ip = js.at(workflow_all_funcs_ip);//得到所有函数对应的ip,这个有点像python中的dict ,key是函数名，value是ip
     
      std::string workflow_parent_cnt  = workflow_name_ + "_parent_cnt"; 
      auto parent_cnt = js.at(workflow_parent_cnt);//记录workflow所有函数的父节点个数，这个有点像python中的dict 
//      LOG(INFO) <<" workflow_name:"<<workflow_name_ <<"  and all_funcs_size:" << all_funcs_size ;
      
      std::string workflow_next = workflow_name_ + "_next";
      auto func_next = js.at(workflow_next);//记录workflow中所有函数的子节点，key是一个str,value是一个list 
   //   LOG(INFO)<<"workflow_name:"<<workflow_name_ <<" and workflow_next:"<<workflow_next;

      std::string workflow_input = workflow_name_ +"_input";
      auto func_input = js.at(workflow_input);//记录workflow中所有函数的输入,key是一个str,value是一个list
    //  LOG(INFO)<<"workflow_name:"<<workflow_name_ <<" and workflow_input:" << workflow_input;

      std::string workflow_output = workflow_name_ + "_output";
      auto func_output = js.at(workflow_output);//记录workflow中所有函数的输出，key是str，value是一个dict 
 //     LOG(INFO)<<"workflow_name:"<<workflow_name_ <<  " and workflow_output:"<<workflow_output;

      std::string workflow_runtime = workflow_name_ +"_runtime";
      auto func_runtime = js.at(workflow_runtime);//记录workflow中所有函数的runtime,key是str,value是float/double 
  //    LOG(INFO)<<"workflow_name:"<<workflow_name_ <<  " and workflow_runtime:" << workflow_runtime ; //<<workflow_output;


      std::string workflow_all_ips = workflow_name_ + "_all_ips";
   //   LOG(INFO)<<"workflow_name:"<<workflow_name_ <<  " and workflow_all_ips:" << workflow_all_ips ; //<<workflow_output;

      auto all_ips = js.at(workflow_all_ips);
      if(all_ips.is_array()) {
          auto all_ips_size = all_ips.size();
          auto i = 0;
          all_ips_.resize(all_ips_size);
          for(i = 0; i < all_ips_size;i++) {
          //    LOG(INFO) <<"workflow_name:" << workflow_name_ <<" and ips:"<< all_ips[i];
              all_ips_[i] = all_ips[i];
          }
      }
    //  LOG(INFO)<<"workflow_name:"<<workflow_name_ << " and all_ips ok" ;
      for(size_t i = 0; i < all_funcs_size;i++) {
          std::string func_name = all_funcs[i];
          std::string func_ip = all_funcs_ip.at(func_name);
          int cnt = parent_cnt.at(func_name);
          parent_cnt_[func_name] = cnt;
      //    LOG(INFO)<<"this func_name:"<< func_name;
     //     LOG(INFO)<<"this func_name:" << func_name << " its ip:" << func_ip ;
    //      LOG(INFO)<<"this_func_name:" << func_name << " its parenct_cnt:" << cnt ;

          all_funcs_.push_back(func_name);
          func_ip_[func_name] = func_ip;

          auto next = func_next.at(func_name);
      //    LOG(INFO) <<" the func_name:"<<func_name << " next is array:"<<next.is_array() ;
          if(next.is_array()) {
              auto next_size = next.size();
            //  LOG(INFO) <<" the func_name:"<<func_name <<"  and next_size:" << next_size ;
              std::vector<std::string> next_funcs;
              if(next_size != 0 ) {
                  next_funcs.resize(next_size);
             //     LOG(INFO) <<" the func_name:" << func_name << " has next";
                  auto i  = 0; 
                  for(i =  0; i < next_size; i++) {
                      std::string next_name = next[i];
              //        LOG(INFO) <<" the  func_name:"<<func_name <<" and next_name:"<<next_name;
                      next_funcs[i] = next_name;
                  }
                  funcs_next_[func_name] = next_funcs;
              //   LOG(INFO) <<" the func_name:" << func_name << " and its son size:"<<next_size ;
              } else {
                  next_funcs.resize(0);
                  funcs_next_[func_name] = next_funcs;
              }
          }

          auto my_input = func_input.at(func_name);
          if(my_input.is_array()) {
              auto input_size = my_input.size();
             // LOG(INFO) <<" the func_name:" << func_name << " and its input is array " << " and its input_size:" << input_size;
              std::vector<std::string> inputs;
              inputs.resize(input_size);
              if(input_size != 0) {
                  auto i = 0;
                  for(i = 0; i < input_size; i++) {
                      std::string input_name = my_input[i];
               //       LOG(INFO) <<"the func_name:"<<func_name <<" and its input:"<<input_name ; 
                      inputs[i] = input_name;
                  }
                  funcs_input_[func_name] = inputs;
              }
          }

         //注:my_output是一个dict 
          auto my_output = func_output.at(func_name);
          std::map<std::string,int> this_func_name_output;
          this_func_name_output.clear();
          for(const auto & item:my_output.items()) {
              std::string key = item.key();
              int size = item.value();
              this_func_name_output[key] = size;
        //      L
          }
          funcs_output_[func_name] = this_func_name_output;
          auto runtime = func_runtime.at(func_name);
          if(runtime.is_number_float() || runtime.is_number_integer()) {
       //       LOG(INFO)<<" the func_name:" << func_name <<" and its runtime:" << runtime;
              funcs_runtime_[func_name] =(float) runtime;
          }
      }
  //设置function的set_function
  function_manager_->set_function(all_funcs_);
}

void WorkerSPManager::set(const std::string &host_addr, const std::string &workflow_name, const uint64_t &min_port) {
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
            //function_manager_ = FunctionManager(workflow_name,workflow_image_name,min_port);
    function_manager_->set(workflow_name,workflow_image_name,min_port);
}

void WorkerSPManager::trigger_function(WorkflowState * state, const std::vector<std::string> & start_functions){
    if(start_functions.empty()) {
        return ;
    }
    //TODO:可以保证start functions都在这台机器跑
    std::vector<std::thread> jobs;
    auto i = 0;
    
    //先启动所有start functions
    for(auto start_func:start_functions) {
        LOG(INFO)<<"1 WorkerSPManager::trigger_function, i: " << i  << " workflow_name:"<< workflow_name_  << " and start_func:" << start_func <<" and state->request_id:"<<state->get_request_id() ;
        //LOG(INFO)<<"1.2 WorkerSPManager::trigger_function,state->request_id:"<<state->get_request_id() ;
        i = i +1;
        state->set_funcs_executed_state(start_func);
        jobs.push_back(std::thread(&WorkerSPManager::trigger_local_function,this ,state, start_func,host_addr_));
    }

    //启动start function的所有子节点函数
    for(auto start_func:start_functions) {
        //TODO
        std::vector<std::string> next_funcs = funcs_next_[start_func];//表示start_funcs的子节点函数
        //启动子函数
        for(auto next_func:next_funcs) {
          std::string ip = func_ip_[next_func];
          LOG(INFO)<<"2 WorkerSPManager::trigger_function,the ip:"<<ip << " and host_addr_:"<<host_addr_ ;
          if(ip == host_addr_) {
              //在这台机器跑
              auto exeucted_status = state->get_funcs_executed_state(next_func);
              LOG(INFO) <<" 3 WorkerSPManager::trigger_function in local , the workflow_name:" << workflow_name_ <<" and next_func:"<<next_func  <<" ip:" << ip << "  and host_addr:" << host_addr_ <<" and exeuted_status:"<<exeucted_status;
              if(exeucted_status) {
                  continue;//已经被启动了，这种情况一般出现在某函数A有多个父节点函数，且这些父节点跟它在同一台机器上
              }
              state->set_funcs_executed_state(next_func);
              jobs.push_back(std::thread(&WorkerSPManager::trigger_local_function,this ,state,next_func,host_addr_));
          } else {
              //在远端机器跑
              auto remote_status = state->get_funcs_remote_state(next_func);
              if(remote_status) {
                  //当remote_status为true时，表示已经被启动了，这种情况适合于某个子节点有多个父节点，其多个父节点在一台机器上，所以可能导致出现多次启动子节点，避免这种情况
                  continue;
              }
              state->set_funcs_remote_state(next_func);//设置状态
              LOG(INFO) <<" 4 WorkerSPManager::trigger_function in remote , the workflow_name:" << workflow_name_ <<" and next_func:"<<next_func  <<" ip:" << ip << "  and host_addr:" << host_addr_;
              jobs.push_back(std::thread(&WorkerSPManager::trigger_remote_function,this ,state,next_func,ip));
          }

        }
    }

    size_t size = jobs.size();
    for(size_t i = 0; i < size; i++) {
        jobs[i].join();
    }

}


void WorkerSPManager::trigger_remote_function(WorkflowState  * state,const std::string &  function_name,const std::string & func_ip){
 //TODO:给远端机器发post请求，触发函数运行

    
    Json js;
    LOG(INFO) <<" 5 WorkerSPManager::trigger_remote_function,the workflow_name:"<<workflow_name_ <<" func_ip:"<< func_ip <<" and function_name:"<<function_name;
    LOG(INFO)<<"6 WorkerSPManager::trigger_remote_function,state->request_id:"<<state->get_request_id() ;
    std::string request_id = state->get_request_id();
    js["request_id"] = request_id;
    //LOG(INFO)<<"1 request_id:"<<request_id ;
    js["workflow_name"] = workflow_name_;
   // LOG(INFO) <<" 2 workflow_name:"<<workflow_name_;
    js["function_name"] = function_name;
   // LOG(INFO) <<"3 function_name:"<<function_name;
    std::string remote_url ="http://" +  func_ip  +"/request";
  //  LOG(INFO) << "4 remote_url:"<<remote_url ;
    state_remote_mutex_.unlock();
   // LOG(INFO) <<"5 js.dump" << js.dump() ;
    auto r = cpr::Post(cpr::Url{remote_url},cpr::Body{js.dump()},cpr::Header{{"Content-Type", "application/json"}});

    LOG(INFO) << "WorkerSPManager::trigger_remote_function,r.Status code:"<<r.status_code ;
}

void WorkerSPManager::trigger_local_function(WorkflowState *  state,const std::string & function_name, const std::string  & func_ip) {
 //TODO:调用run_function
  //  state->acquire();
    LOG(INFO) <<"7 WorkerSPManager::trigger_local_function,the workflow_name:"<<workflow_name_ <<" func_ip:"<< func_ip <<" and function_name:"<<function_name;
    LOG(INFO)<<"8 WorkerSPManager::trigger_local_function,state->request_id:"<<state->get_request_id()  <<" function_name:"<<function_name;
    run_function(state,function_name,func_ip);
    return ;

}


void WorkerSPManager::trigger_local_remote_function(WorkflowState *  state,const std::string & function_name, const std::string  & func_ip) {
 //TODO:调用run_function
  //  state->acquire();
    state_executd_mutex_.lock();
    auto exeucted_status = state->get_funcs_executed_state(function_name);
    LOG(INFO) <<"9 WorkerSPManager::trigger_local_remote_function,the workflow_name:"<<workflow_name_ <<" func_ip:"<< func_ip <<" and function_name:"<<function_name <<" its exeuted_status:"<<exeucted_status;
    LOG(INFO)<<"10 WorkerSPManager::trigger_local_remote_function,state->request_id:"<<state->get_request_id()  <<" function_name:"<<function_name;
    if(exeucted_status ) {
        state_executd_mutex_.unlock();
        return ;//这个函数已经被启动了，可能出现的情况是，函数A有多个父节点B/C,其中B跟A机器上，假设B先启动了A，然后C通过post请求想启动A，发现A启动了，直接返回
    }
    state->set_funcs_executed_state(function_name);//设置状态
    state_executd_mutex_.unlock();
    run_function(state,function_name,func_ip);
    return ;

}

void WorkerSPManager::run_function(WorkflowState * state,const std::string & function_name, const std::string & func_ip) {
    //TODO,启动函数
    LOG(INFO)<<"11 WorkerSPManager::run_function,the workflow_name:"<<workflow_name_ <<" func_ip:"<< func_ip <<" and function_name:"<<function_name;
    std::string request_id = state->get_request_id();
    float runtime = funcs_runtime_[function_name];//函数的运行时间
    std::vector<std::string> input = funcs_input_[function_name];
    std::map<std::string ,int> output = funcs_output_[function_name];
    auto start = std::chrono::system_clock::now();
    function_manager_->run_function(function_name, request_id, runtime, input, output);//同步运行函数
    auto end = std::chrono::system_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    double run_times  =  double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den ;
    LOG(INFO)<<"12 WorkerSPManager::run_function,the function_name:"<< function_name <<" and run_time:"<<run_times <<" and function runtime"<< runtime; 
    //启动孙子函数  
    std::vector<std::string> next_func_list = funcs_next_[function_name];
    std::vector<std::thread> jobs;
    auto next_func_list_size = next_func_list.size();
    auto i = 0; 
    for(i = 0; i < next_func_list_size; i++) {
        std::string next_func  = next_func_list[i];
        std::vector<std::string> next_next_func_list = funcs_next_[next_func];
        LOG(INFO) <<"13  WorkerSPManager::run_function,the next_next_func_list.size:"<<next_next_func_list.size() <<" and function_name:"<<function_name <<" and next_func:"<<next_func;
        auto next_next_func_list_size = next_next_func_list.size();
        auto j = 0;
        for( j = 0; j < next_next_func_list_size; j++) {
            //state->acquire();
            std::string next_next_func = next_next_func_list[j];
            std::string next_next_func_ip = func_ip_[next_next_func];
            if(next_next_func_ip == host_addr_) {
                //在同一台机器上
                auto executd_status = state->get_funcs_executed_state(next_next_func);
                LOG(INFO)<<"14 WorkerSPManager::run_functon trigger_local_function,next_next_func:"<<next_next_func <<" and function_name:"<<function_name <<" and exeucted_status"<< executd_status <<" and next_func:"<<next_func << " and func_ip:"<<func_ip << " and next_next_func_ip:"<<next_next_func_ip;
                if(executd_status) {
                    continue;//已经被启动了
                }
                state->set_funcs_executed_state(next_next_func);
                jobs.push_back(std::thread(&WorkerSPManager::trigger_local_function,this,state,next_next_func,host_addr_));
            } else  {
                //在不同的机器上
                auto remote_status = state->get_funcs_remote_state(next_next_func);
                LOG(INFO)<<"15 WorkerSPManager::run_functon trigger_remote_function,next_next_func:"<<next_next_func  <<" and function_name:"<<function_name << " and  remote_status" << remote_status << " and next_func:"<<next_func << " and next_next_func_ip:"<<next_next_func_ip ;
                if(remote_status) {
                        continue;
                }
                state->set_funcs_remote_state(next_next_func);
                jobs.push_back(std::thread(&WorkerSPManager::trigger_remote_function,this,state,next_next_func,next_next_func_ip));
            }  
        }
    }
    auto job_size = jobs.size();
    for(auto i  = 0; i < job_size;i++) {
        jobs[i].join();//等待线程完成
    }
}
