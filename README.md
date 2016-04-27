# sam, Service Available Monitor
=========================================

##  功能说明
```
业务进程、端口监控，业务可用性监控（web），并告警
```

## 使用方法
```
1）配置文件
etc/sam.conf，每个配置项参考配置文件的说明
2）启动、停止、重启
python sam.py -a start
python sam.py -a stop
python sam.py -a restart
```

## 要点：
```
1）日志路径
/tmp/service_available_monitor.log
2）扩展
写一个简单的web portal，将监控配置写入到DB；
sam.py中修改获取数据源的方式，例如通过http api；
```

## 技术交流
```
QQ: 86877295
```
