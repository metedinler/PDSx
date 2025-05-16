
# === APPEND THIS TO pdsXv14u.py ===
# -------- PART 2 : ADVANCED COMMANDS (items 7-11) -------------
import gzip, base64, types

def _encode_gzip(data:bytes)->bytes:
    return gzip.compress(data)
def _decode_gzip(data:bytes)->bytes:
    return gzip.decompress(data)

# Extend existing Interpreter
def _inject_part2(cls):
    # ---------- SAVE / LOAD (gzip) ----------
    def cmd_SAVE(self,arg):
        path=arg.strip().strip('"')
        state={'vars':self.vars,'mem':_pool._heap}
        with gzip.open(path,'wb') as f:
            f.write(json.dumps(state,default=lambda o:o.hex() if isinstance(o,bytearray) else o).encode())
        print("STATE SAVED",path)
    def cmd_LOAD(self,arg):
        path=arg.strip().strip('"')
        with gzip.open(path,'rb') as f:
            state=json.loads(f.read().decode())
        self.vars=state['vars']
        _pool._heap={int(k):bytearray.fromhex(v) for k,v in state['mem'].items()}
        print("STATE LOADED",path)
    cls.cmd_SAVE=cmd_SAVE; cls.cmd_LOAD=cmd_LOAD

    # ---------- ENUM ----------
    def cmd_ENUM(self,arg):
        name,body=arg.split('=',1)
        mapping={}
        for item in body.strip('{} ').split(','):
            k,v=item.split('=')
            mapping[k.strip()]=int(v)
        self.vars[name.strip()]=EnumInstance(mapping)
    cls.cmd_ENUM=cmd_ENUM

    # ---------- ARRAY ----------
    def cmd_ARRAY(self,arg):
        # ARRAY arr = [1,2,3]   or ARRAY arr 5
        if '=' in arg:
            name,body=[x.strip() for x in arg.split('=',1)]
            arr=[self.val(v.strip()) for v in body.strip('[] ').split(',')]
        else:
            name,size=arg.split()
            arr=[0]*int(size)
        self.vars[name]=ArrayInstance(arr)
    cls.cmd_ARRAY=cmd_ARRAY

    # ---------- STACK advanced ----------
    def cmd_STACK(self,arg):
        name,op,*rest=arg.split()
        dq=self.stacks[name]
        op=op.upper()
        if op=='PUSH': dq.append(self.val(rest[0]))
        elif op=='POP': print(dq.pop())
        elif op=='PEEK': print(dq[-1] if dq else None)
        elif op=='SWAP': dq[-1],dq[-2]=dq[-2],dq[-1]
        elif op=='CLEAR': dq.clear()
    cls.cmd_STACK=cmd_STACK

    # ---------- INLINE REPLY / C / ASM ----------
    def cmd_INLINE(self,arg):
        mode,arg=arg.split(None,1)
        mode=mode.upper()
        code=[]
        self.pc+=1
        while self.pc < len(self.lines) and not self.lines[self.pc].upper().startswith('ENDINLINE'):
            code.append(self.lines[self.pc])
            self.pc+=1
        if mode=='REPLY':
            print('\n'.join(code))
        elif mode in ('C','ASM'):
            open(f'inline_{mode.lower()}.txt','w').write('\n'.join(code))
            print(f'INLINE {mode} code written to inline_{mode.lower()}.txt')
        # ENDINLINE satırını ana döngü atlayacak
    cls.cmd_INLINE=cmd_INLINE
_inject_part2(PdsXv14uInterpreter)
