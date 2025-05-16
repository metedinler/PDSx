
# === APPEND THIS TO pdsXv14u.py ===
# -------- PART 5 : Checkpoint, Thread/Async, Web API+, Logging, Lang.json (items 26-30) -------------
import asyncio, threading, datetime, uuid, requests, logging, json

# --- helper for async tasks
_async_tasks={}
_thread_tasks={}

def _inject_part5(cls):
    # ------ CHECKPOINT ------------
    def _stamp(): return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    def cmd_CHECKPOINT(self,arg):
        path=arg.strip().strip('"')
        if not path: path=f'ckp_{_stamp()}.gz'
        # reuse SAVE implementation
        self.cmd_SAVE(path)
    cls.cmd_CHECKPOINT=cmd_CHECKPOINT

    # ------ THREAD command ----------
    def _runner(interp,line):
        try: interp.exec_line(line)
        except Exception as e: logging.error("THREAD err: %s",e)
    def cmd_THREAD(self,arg):
        sub,*rest=arg.split(None,1)
        if sub.upper()=='RUN':
            code=rest[0].strip('"')
            t=threading.Thread(target=_runner,args=(self,code),daemon=True)
            t.start()
            _thread_tasks[id(t)]=t
            print('THREAD',id(t),'STARTED')
        elif sub.upper()=='JOIN':
            tid=int(rest[0])
            t=_thread_tasks.get(tid); t.join()
    cls.cmd_THREAD=cmd_THREAD

    # ------ ASYNC command ----------
    async def _async_eval(interp,expr,aid):
        try:
            res=eval(expr,{},interp.vars)
            _async_tasks[aid]=res
        except Exception as e:
            _async_tasks[aid]=e
    def cmd_ASYNC(self,arg):
        sub,*rest=arg.split(None,1)
        if sub.upper()=='RUN':
            aid=str(uuid.uuid4())[:8]
            expr=rest[0].strip('"')
            asyncio.create_task(_async_eval(self,expr,aid))
            print('TASK',aid,'STARTED')
        elif sub.upper()=='WAIT':
            aid=rest[0]
            while aid not in _async_tasks: time.sleep(0.05)
            print('TASK',aid,'RESULT',_async_tasks[aid])
    cls.cmd_ASYNC=cmd_ASYNC

    # ------ Web API+ -------------
    def _req(method,url,headers=None,data=None):
        return requests.request(method,url,headers=headers,data=data,timeout=10).text[:500]
    def cmd_API(self,arg):
        # API METHOD URL [JSON]
        parts=arg.split(None,2)
        method=parts[0].upper(); url=parts[1].strip('"')
        payload=json.loads(parts[2]) if len(parts)==3 else None
        print(_req(method,url,data=json.dumps(payload) if payload else None))
    cls.cmd_API=cmd_API

    # ------ LOG command -----------
    def cmd_LOG(self,arg):
        sub,*rest=arg.split()
        if sub.upper()=='LEVEL':
            lvl=rest[0].upper()
            logging.getLogger().setLevel(getattr(logging,lvl,logging.INFO))
            print('LOG LEVEL',lvl)
    cls.cmd_LOG=cmd_LOG

    # ------ HELP / LANG.json -------
    _lang_cache={}
    def cmd_HELP(self,arg):
        lang='en'
        if ':' in arg:
            lang,topic=[x.strip() for x in arg.split(':',1)]
        else:
            topic=arg.strip()
        if lang not in _lang_cache:
            try:
                _lang_cache[lang]=json.load(open(f'lang_{lang}.json',encoding='utf-8'))
            except FileNotFoundError:
                _lang_cache[lang]={}
        print(_lang_cache[lang].get(topic,'No help'))
    cls.cmd_HELP=cmd_HELP
_inject_part5(PdsXv14uInterpreter)
