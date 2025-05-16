
# === APPEND THIS TO pdsXv14u.py ===
# -------- PART 3 : NLP, PROLOG V3, TREE/GRAPH (items 12-15) -------------
try:
    import nltk, math, itertools
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    nltk = None

# ------- Tree & Graph data structures -------
class TreeNode:
    __slots__=("value","children")
    def __init__(self,val): self.value=val; self.children=[]
    def add(self,node): self.children.append(node)
class Graph:
    def __init__(self): self.edges=defaultdict(list)
    def add_edge(self,u,v): self.edges[u].append(v)
    def bfs(self, start):
        seen=set([start]); q=deque([start])
        while q:
            u=q.popleft(); yield u
            for v in self.edges[u]:
                if v not in seen:
                    seen.add(v); q.append(v)

# ------- enhance Interpreter -------
def _inject_part3(cls):
    # NLP tokenize / lower / stopword removal
    def _simple_tokens(text:str):
        if nltk: 
            tok=word_tokenize(text)
            sw=set(stopwords.words('english')) if nltk else set()
            return [t.lower() for t in tok if t.isalpha() and t.lower() not in sw]
        return [w.lower() for w in re.findall(r'[A-Za-z]+',text)]

    def cmd_TOKENIZE(self,arg):
        txt=self.val(arg)
        self.vars['_TOK']=_simple_tokens(txt)
        print(self.vars['_TOK'])
    cls.cmd_TOKENIZE=cmd_TOKENIZE

    def cmd_EMBED_VEC(self,arg):
        if '_TOK' not in self.vars: print('TOKENIZE first'); return
        vec=[hash(w)%1000 for w in self.vars['_TOK']]
        self.vars['_VEC']=vec
        print('VEC',vec[:10],'...')
    cls.cmd_EMBED_VEC=cmd_EMBED_VEC

    # Graph commands
    def cmd_GRAPH(self,arg):
        name,op,*rest=arg.split()
        g=self.vars.setdefault(name,Graph())
        if op.upper()=='ADD':
            g.add_edge(rest[0],rest[1])
        elif op.upper()=='BFS':
            print(list(g.bfs(rest[0])))
    cls.cmd_GRAPH=cmd_GRAPH

    # Tree commands
    def cmd_TNODE(self,arg):
        name,val=[x.strip() for x in arg.split('=',1)]
        self.vars[name]=TreeNode(self.val(val))
    cls.cmd_TNODE=cmd_TNODE
    def cmd_TADD(self,arg):
        parent,child=arg.split()
        self.vars[parent].add(self.vars[child])
    cls.cmd_TADD=cmd_TADD

    # PROLOG backtracking (simplified)
    def _unify(a,b,theta):
        if theta is None: return None
        if a==b: return theta
        if isinstance(a,str) and a.startswith('?'):
            theta[a]=b; return theta
        if isinstance(b,str) and b.startswith('?'):
            theta[b]=a; return theta
        return None
    def _resolve(goal,facts):
        for fact in facts:
            theta={}
            parts_fact=fact.split()
            parts_goal=goal.split()
            if len(parts_fact)!=len(parts_goal): continue
            ok=True
            for x,y in zip(parts_goal,parts_fact):
                theta=_unify(x,y,theta)
                if theta is None: ok=False; break
            if ok: yield theta
    def cmd_PFORALL(self,arg):
        res=list(_resolve(arg.strip(),self.prolog.facts))
        print('SOLUTIONS',res)
    cls.cmd_PFORALL=cmd_PFORALL
_inject_part3(PdsXv14uInterpreter)
