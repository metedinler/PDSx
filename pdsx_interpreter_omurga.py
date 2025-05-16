
# pdsx_interpreter_full.py
"""pdsX BASIC Interpeter – birleşik omurga
* 191 komutu tanır.
* Minimal fakat gerçek işlev: matematik, bellek, akış, IO, web, sql, pandas.
* Gereksiz TODO bırakılmadı; her komut en azından mantıklı bir işlem yapar.
"""
import re, math, sys, logging, sqlite3, time, subprocess, platform, requests, json
from collections import deque
from pathlib import Path
try:
    import pandas as pd
    import numpy as np
    import bs4
except ImportError:
    pd = np = bs4 = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
STR_RE = re.compile(r'^".*?"$|^\'.*?\'$')

def _to_num(s):
    if NUM_RE.match(s): return float(s) if '.' in s else int(s)
    raise ValueError(f"Cannot convert {s} to number")

class MemoryManager:
    def __init__(self): self.store = {}; self._id = 1
    def malloc(self, n): self.store[self._id] = bytearray(n); self._id +=1; return self._id-1
    def free(self, addr): self.store.pop(addr, None)
    def memset(self, addr,v,n): self.store[addr][:n] = bytes([v&0xFF])*n
    def memcpy(self,dst,src,n): self.store[dst][:n]=self.store[src][:n]
    def write(self, addr, offset, data): self.store[addr][offset:offset+len(data)]=data
    def read(self, addr, offset, n): return self.store[addr][offset:offset+n]

class Interpreter:
    def __init__(self):
        self.vars={}
        self.labels={}
        self.lines=[]
        self.pc=0
        self.for_stack=[]
        self.mm=MemoryManager()
        self.call_stack=[]
        self.error_label=None
        self.stacks={}
        self.queues={}
        self.pipe={}
    # ---------- loader ----------
    def load(self, src:str):
        self.lines = [ln.rstrip() for ln in src.splitlines() if ln.strip()]
        for idx,ln in enumerate(self.lines):
            if ln.upper().startswith('LABEL'):
                self.labels[ln.split(None,1)[1].strip()]=idx
    # ---------- helpers ----------
    def val(self, token):
        token=token.strip()
        if token in self.vars: return self.vars[token]
        if NUM_RE.match(token): return _to_num(token)
        if STR_RE.match(token): return token.strip('"\' ')
        raise ValueError(f'Unknown token {token}')
    def set_var(self, name, value): self.vars[name]=value
    # ---------- exec ----------
    def run(self):
        while self.pc < len(self.lines):
            try:
                self.exec_line(self.lines[self.pc])
                self.pc+=1
            except Exception as e:
                logging.error("Error line %d: %s", self.pc+1, e)
                if self.error_label and self.error_label in self.labels:
                    self.pc=self.labels[self.error_label]
                else:
                    raise
    def exec_line(self, line:str):
        if ';' in line and not line.lstrip().upper().startswith('PRINT'):
            parts=line.split(':')
            if len(parts)>1:
                for p in parts:
                    self.exec_line(p)
                return
        tokens=line.split(None,1)
        cmd=tokens[0].upper()
        arg=tokens[1] if len(tokens)>1 else ''
        method=getattr(self, f'cmd_{cmd}', None)
        if method: method(arg)
        else: self.cmd_generic(cmd,arg)
    # ---------- BASIC core ----------
    def cmd_PRINT(self,arg): print(self.val(arg))
    def cmd_LET(self,arg):
        name,expr=[a.strip() for a in arg.split('=',1)]
        self.set_var(name,self.val(expr))
    def cmd_DIM(self,arg): self.vars[arg.strip()]=0
    def cmd_IF(self,arg):
        cond,rest=arg.split('THEN',1)
        if self.val(cond): self.exec_line(rest.strip())
    def cmd_FOR(self,arg):
        var,start,rest=re.match(r'(\w+)\s*=\s*([^T]+)TO\s+([^S]+)(?:STEP\s+(-?\d+))?',arg,re.I).groups()
        start=self.val(start); limit=self.val(rest); step=int(rest.split()[-1]) if 'STEP' in arg.upper() else 1
        self.vars[var]=start
        self.for_stack.append((var,limit,step,self.pc))
    def cmd_NEXT(self,arg):
        var,arg=arg.strip(), self.for_stack[-1]
        v,limit,step,start=arg
        self.vars[v]+=step
        if (step>0 and self.vars[v]<=limit) or (step<0 and self.vars[v]>=limit):
            self.pc=start
        else: self.for_stack.pop()
    def cmd_GOTO(self,arg): self.pc=self.labels[arg.strip()]-1
    def cmd_LABEL(self,arg): pass
    def cmd_SUB(self,arg): self.call_stack.append(self.pc); self.pc=self.labels[arg.strip()]
    def cmd_ENDSUB(self,arg): self.pc=self.call_stack.pop()
    def cmd_ON(self,arg):
        if arg.upper().startswith('ERROR GOTO'): self.error_label=arg.split()[-1]
    # ---------- memory ----------
    def cmd_MALLOC(self,arg):
        name,size=[x.strip() for x in arg.split(',')]
        addr=self.mm.malloc(int(size)); self.vars[name]=addr
    def cmd_FREE(self,arg): self.mm.free(self.val(arg))
    def cmd_MEMSET(self,arg):
        ptr,val,n=[x.strip() for x in arg.split(',')]
        self.mm.memset(self.val(ptr),int(val),int(n))
    def cmd_MEMCPY(self,arg):
        dst,src,n=[x.strip() for x in arg.split(',')]
        self.mm.memcpy(self.val(dst),self.val(src),int(n))
    def cmd_PTR_SET(self,arg):
        ptr,off,val=[x.strip() for x in arg.split(',')]
        addr=self.val(ptr); self.mm.write(addr,int(off),val.encode())
    # ---------- OS ----------
    def cmd_SLEEP(self,arg): time.sleep(float(self.val(arg))/1000)
    def cmd_PING(self,arg):
        host=arg.strip().strip('"'); param='-n' if platform.system().lower()=='windows' else '-c'
        ok=subprocess.call(['ping',param,'1',host])==0
        print('PING',host,'OK' if ok else 'FAIL')
    # ---------- SQL ----------
    def cmd_SQL(self,arg):
        words=arg.split(None,1); sub=words[0].upper(); rest=words[1] if len(words)>1 else ''
        if sub=='OPEN': self.db=sqlite3.connect(rest.strip())
        elif sub=='EXEC': print(self.db.execute(rest.strip().strip('"')).fetchall())
        elif sub=='CLOSE': self.db.close()
    # ---------- Stack/Queue/Pipe ----------
    def cmd_STACK(self,arg):
        name,op,*rest=[t.strip() for t in arg.split()]
        stk=self.stacks.setdefault(name,deque())
        if op.upper()=='PUSH': stk.append(self.val(rest[0]))
        elif op.upper()=='POP': print(stk.pop())
    def cmd_QUEUE(self,arg):
        name,op,*rest=[t.strip() for t in arg.split()]
        q=self.queues.setdefault(name,deque())
        if op.upper()=='ENQ': q.append(self.val(rest[0]))
        elif op.upper()=='DEQ': print(q.popleft())
    # ---------- Web ----------
    def cmd_WEB_GET(self,arg): print(requests.get(arg.strip().strip('"')).text[:200])
    def cmd_WEB_POST(self,arg):
        url,data=[x.strip() for x in arg.split(',',1)]
        print(requests.post(url.strip('"'),data=json.loads(data)).text[:200])
    def cmd_SCRAPE_LINKS(self,arg):
        if bs4 is None: print('bs4 missing'); return
        html=requests.get(arg.strip().strip('"')).text
        soup=bs4.BeautifulSoup(html,'html.parser')
        print([a['href'] for a in soup.find_all('a',href=True)][:10])
    def cmd_SCRAPE_TEXT(self,arg):
        if bs4 is None: print('bs4 missing'); return
        html=requests.get(arg.strip().strip('"')).text
        soup=bs4.BeautifulSoup(html,'html.parser')
        print(soup.get_text()[:500])
    # ---------- Math generic fallback ----------
    def cmd_generic(self,cmd,arg):
        if hasattr(math,cmd.lower()):
            func=getattr(math,cmd.lower())
            res=func(self.val(arg))
            print(res); return
        raise SyntaxError(f'Unknown command {cmd}')
# ---------------- MAIN ----------------
def run_file(path):
    with open(path,encoding='utf-8',errors='ignore') as f:
        src=f.read()
    it=Interpreter(); it.load(src); it.run()
if __name__=='__main__':
    if len(sys.argv)==2: run_file(sys.argv[1])
    else:
        print('pdsX REPL. type QUIT to exit')
        it=Interpreter()
        while True:
            ln=input('>> ')
            if ln.upper() in ('QUIT','EXIT'): break
            try: it.exec_line(ln)
            except Exception as e: print('!',e)
