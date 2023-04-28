import logging 

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
# 建立一个filehandler来把日志记录在文件里，级别为debug以上
fh = logging.FileHandler("../workflow_manager/debug.log")

fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')

ch.setFormatter(formatter)
fh.setFormatter(formatter)
#将相应的handler添加在logger对象中
log.addHandler(ch)
log.addHandler(fh)