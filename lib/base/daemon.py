# -*- encoding=utf-8 -*-
import sys
import os
import atexit
import traceback
from signal import SIGTERM 

class daemon:
    def __init__(self, pidfile, stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'):
        # 需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
  
    def _daemonize(self):
        try: 
          pid = os.fork() 
          if pid > 0:
            sys.exit(0) # 退出主进程
        except OSError, e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)
  
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
      
        # 创建子进程
        try: 
            pid = os.fork() 
            if pid > 0:
                sys.exit(0) 
        except OSError, e: 
                sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
                sys.exit(1) 
        
        try:
            # 重定向文件描述符
            sys.stdout.flush()
            sys.stderr.flush()
            si = file(self.stdin, 'r')
            so = file(self.stdout, 'a+')
            se = file(self.stderr, 'a+', 0)
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
            
            # 创建processid文件
            atexit.register(self.delpid)
            pid = str(os.getpid())
            file(self.pidfile, 'w+').write('%s\n' % pid)
            sys.stdout.write('Daemon Start! Pid Is: %s\n' % (pid))
        except Exception, expt:
            sys.stderr.write(traceback.format_exc())
  
    def delpid(self):
        os.remove(self.pidfile)

    def start(self, func, *args, **kwargs):
        # 检查pid文件是否存在以探测是否存在进程
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        
        if pid:
            message = 'Pidfile %s Already Exist. Daemon Already Running?\n'
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
            
        # 启动监控
        self._daemonize()
        func(*args, **kwargs)
        

    def stop(self):
        # 从pid文件中获取pid
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        
        if not pid:
            message = 'Pidfile %s Do Not Exist. Daemon Not Running?\n'
            sys.stderr.write(message % self.pidfile)
            return  # 重启不报错
        
        # 杀进程
        try:
            sys.stderr.write("Daemon Stop! Pid Is: %s\n" % (pid))
            os.kill(pid, SIGTERM)
            os.remove(self.pidfile)
        except OSError, err:
            err = str(err)
            if err.find('No Such Process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self, func, *args, **kwargs):
        self.stop()
        self.start(func, *args, **kwargs)
        
# if __name__ == "__main__":
#     daemon("/tmp/service_available.pid").start(main, confpath, env)