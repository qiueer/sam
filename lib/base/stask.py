#encoding=UTF8
'''
Simple Task
@author: Qiueer
'''

from threading import Thread
import Queue

class tqueue(Queue.Queue):
    
    def __init__(self, workers=5, maxsize=0):
        #super(TQueue, self).__init__(maxsize=maxsize)
        Queue.Queue.__init__(self, maxsize=maxsize)
        self._workers = workers
        self._start_workers()
        
    def add_task(self, task, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))
        
    def _start_workers(self):
        for i in xrange(self._workers):
            t = Thread(target=self._worker)
            t.setDaemon(True) #后台，完成后自动删除
            t.start()
            
    def _worker(self):
        while True:
            task,args,kwargs = self.get()
            task(*args, **kwargs)
        self.task_done()
        