## 记录cold start latency
第一次跑和第二次跑的时间之差记为cold start latency， 50MB/s, 6RPM下跑的

https://github.com/lambda7xx/EagerFlow/blob/FaaSFlow/test/asplos/all_tail_latency-2023-VLDB/workersp-0120-11-23.log

https://github.com/lambda7xx/EagerFlow/blob/FaaSFlow/test/asplos/all_tail_latency-2023-VLDB/mastersp-0120.log

CFlow/FaaSFlow或许需要重跑一次，(2023-02-12)
<!-- 
或者说这个实验需要重下设计下，不设置请求频率，而是在50MB/s下一个一个发送过去，计算第一次e2e时间和第二次e2e时间 -->