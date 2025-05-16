
# === APPEND THIS TO pdsXv14u.py ===
# -------- PART 4 : Pipeline, Event-Timer, Meta, SysInfo, Collection (items 16-25) -------------
import platform, psutil, inspect, asyncio, threading

# -------- Event Timer -------------
class _TimerThread(threading.Thread):
    def __init__(self, interp, interval):
        super().__init__(daemon=True)
        self.interp=interp; self.interval=interval; self.running=True
    def run(self):
        while self.running:
            time.sleep(self.interval)
            self.interp.events.trigger(0)  # slot0 tick

def _inject_part4(cls):
    # GLOBAL timer thread ref
    cls._timer_thread=None

    def cmd_EVENT(self,arg):
        # EVENT SET idx = "PRINT 1" , EVENT TRIGGER idx
        sub,*rest=arg.split(None,1)
        sub=sub.upper()
        if sub=='SET':
            idx,code=[x.strip() for x in rest[0].split('=',1)]
            idx=int(idx); code=code.strip('"')
            self.events.set(idx, lambda: self.exec_line(code))
        elif sub=='TRIGGER':
            idx=int(rest[0]); self.events.trigger(idx)
        elif sub=='START':
            interval=float(rest[0])/1000
            cls._timer_thread=_TimerThread(self,interval); cls._timer_thread.start()
        elif sub=='STOP':
            if cls._timer_thread: cls._timer_thread.running=False
    cls.cmd_EVENT=cmd_EVENT

    # -------- Pipeline commands -----------
    def cmd_PIPE(self,arg):
        sub,*rest=arg.split(None,1)
        sub=sub.upper()
        if sub=='START':
            self.pipeline=Pipeline()
        elif sub=='ADD':
            fn_name,expr=rest[0].split(None,1)
            if fn_name.upper()=='MAP':
                func=lambda x: eval(expr,{},self.vars|{'x':x})
                self.pipeline.add(lambda d,*a,**kw: list(map(func,d)))
            elif fn_name.upper()=='FILTER':
                func=lambda x: eval(expr,{},self.vars|{'x':x})
                self.pipeline.add(lambda d,*a,**kw: [x for x in d if func(x)])
        elif sub=='RUN':
            data=self.vars.get(rest[0].strip(),None)
            self.vars['_PIPE_OUT']=self.pipeline.run(data)
            print('PIPE_OUT',self.vars['_PIPE_OUT'][:10] if isinstance(self.vars['_PIPE_OUT'],list) else self.vars['_PIPE_OUT'])
        elif sub=='CLEAR':
            self.pipeline=Pipeline()
    cls.cmd_PIPE=cmd_PIPE

    # -------- Meta functions ----------
    def cmd_OMEGA(self,arg):
        body=arg.strip('"')
        self.vars['_OMEGA']=lambda *a,**kw: eval(body,{},self.vars|dict(a=a,kw=kw))
        print('OMEGA defined')
    cls.cmd_OMEGA=cmd_OMEGA
    def cmd_GAMMA(self,arg):
        name,expr=[x.strip() for x in arg.split('=',1)]
        self.vars[name]=eval(expr,{},self.vars)
        print('GAMMA',name,'=',self.vars[name])
    cls.cmd_GAMMA=cmd_GAMMA

    # -------- Collection set ops ----------
    def cmd_SETOP(self,arg):
        op,a,b=arg.split()
        sa=set(self.val(a)); sb=set(self.val(b))
        if op.upper()=='UNION': print(sa|sb)
        elif op.upper()=='INTERSECT': print(sa&sb)
        elif op.upper()=='DIFF': print(sa-sb)
    cls.cmd_SETOP=cmd_SETOP

    # -------- System Info ----------
    def cmd_SYSINFO(self,arg):
        info={'platform':platform.platform()}
        try:
            import psutil
            info.update({'cpu':psutil.cpu_percent(),'mem':psutil.virtual_memory().percent})
        except ImportError:
            pass
        print(info)
    cls.cmd_SYSINFO=cmd_SYSINFO

    # -------- Encoding ----------
    def cmd_ENCODING(self,arg):
        sub,*rest=arg.split()
        if sub.upper()=='SET':
            enc=rest[0]; LibXCore.ENCODINGS.insert(0,enc)
        elif sub.upper()=='LIST':
            print(LibXCore.ENCODINGS)
    cls.cmd_ENCODING=cmd_ENCODING
_inject_part4(PdsXv14uInterpreter)
