    #!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters
# PRPE technical version 6

#=============================================================================

import sys
from collections import Counter
from copy import deepcopy
from numpy import argmin

goodroots = Counter()
badroots = {}
goodprefixes = Counter()
badprefixes = {}
goodpostfixes = Counter()
badpostfixes = {}

premaxlen = 8
postmaxlen = 7
minrootlen = 2
minpreflen = 2

def isUlower(word):
    return len(word)>=2 and word[0:1].isupper() and word[1:].islower()

def processUlower(word):
    if isUlower(word):
        return word.lower()
    else: return word

def search_codetree(tword,codetree):
    """ Stored in codetree with non-zero value in the terminal node
    """
    pos = 0
    while True:
        s = tword[pos]
        if s not in codetree:
            return 0
        elif pos==len(tword)-1:
            return codetree[s][0]
        else:
            pos += 1
            codetree = codetree[s][1]
    
def search_codetree_hasleftsub(tword,codetree):
    """ Stored in codetree with non-zero value in any except the terminal node
    """
    pos = 0
    while True:
        s = tword[pos]
        if s not in codetree:
            return 0
        elif codetree[s][0]>0:
            return codetree[s][0]
        elif pos==len(tword)-1:
            return 0
        else:
            pos += 1
            codetree = codetree[s][1]
    
def search_codetree_isleftsub(tword,codetree):
    """ Stored in codetree having any value terminal node (i.e., reaching terminal node)
    """
    pos = 0
    while True:
        s = tword[pos]
        if s not in codetree:
            return 0
        elif pos==len(tword)-1:
            return 1
        else:
            pos += 1
            codetree = codetree[s][1]
    
def add_to_codetree(tword,codetree,freq=1):
    """ Adds one tuple-word to tree structure - one node per symbol
        word end in the tree characterized by node[0]>0
    """
    unique=0
    for pos in range(len(tword)):
        s = tword[pos]
        if s not in codetree:
            codetree[s] = [0,{}]
            unique+=1
        codetree[s][0] += freq
        codetree = codetree[s][1]
    return unique

def add_to_vocab_multi(word,vocab,freq):
    for pos in range(len(word)):
        if not word[pos].isalpha(): return
        vocab[word[:pos+1]] += freq

def add_to_vocab_multi_reverse(word,vocab,postmaxlen,minrootlen,freq):
    """ Adds one tuple-word to tree structure - one node per symbol
        word end in the tree characterized by node[0]>0
    """
    pos = 0
    while pos<len(word)-minrootlen and pos<postmaxlen:
        vocab[word[:pos+1]] += freq
        pos+=1

def add_to_codetree_terminal(tword,codetree,freq=1):
    """ Adds one tuple-word to tree structure - one node per symbol
        word end in the tree characterized by node[0]>0
    """
    for pos in range(len(tword)):
        s = tword[pos]
        if s not in codetree:
            codetree[s] = [0,{}]
        if pos==len(tword)-1:
            codetree[s][0] = freq
        else:
            codetree = codetree[s][1]

def read_codetree(datafile,reverse=False):
    codetree = {}
    for line in datafile:
        item = line.split()
        word = item[0]
        if reverse: word=word[::-1]
        if len(item)>1:
            num = int(item[1])
        else:
            num = 1
        add_to_codetree_terminal(word,codetree,num)
    return codetree

def read_vocabulary(vocabfile,reverse=False):
    vocab = Counter()
    rcounter = 999999999
    for line in vocabfile:
        item = line.split()
        word = item[0]
        if reverse: word=word[::-1]
        if len(item)>1:
            num = int(item[1])
        else:
            num = rcounter
            rcounter-=1
        vocab[word] = num
    return vocab

def extract_vocabulary(infile):
    vocab = Counter()
    for line in infile:
        for word in line.split():
#            word = processMeta(word)
            word = processUlower(word)
            vocab[word] += 1
    return vocab

def save_vocabulary(vocabfile,vocab,order=False,reverseorder=True,alphaonly=False,maxcount=None,vocabout=None):
    cnt = 0
    if order:
        for item in sorted(vocab.items(),key=lambda x: x[1],reverse=reverseorder):
            if maxcount is not None and cnt==maxcount: return
            if not alphaonly or item[0].isalpha():
                vocabfile.write(u"{0} {1}\n".format(item[0],item[1]))
                if vocabout is not None: vocabout[item[0]]=item[1]
                cnt+=1
    else:
        for item in vocab.items():
            if maxcount is not None and cnt==maxcount: return
            if not alphaonly or item[0].isalpha():
                vocabfile.write(u"{0} {1}\n".format(item[0],item[1]))
                if vocabout is not None: vocabout[item[0]]=item[1]
                cnt+=1

def register_subwords(infile,premaxlen,postmaxlen,minrootlen,isvocabin=False,vocabout=None,rawprefixfile=None,rawpostfixfile=None,loadrawfile=False,freqnotrank=False):
    rawprecodetree = {}
    rawpostcodetree = {}
    if isvocabin:
        vocab = read_vocabulary(infile)
    else:
        vocab = extract_vocabulary(infile)
    if loadrawfile:
        rawprevocab = read_vocabulary(rawprefixfile)
        rawpostvocab = read_vocabulary(rawpostfixfile)
    else:
        rawprevocab = Counter()
        rawpostvocab = Counter()
        for item in vocab.items():
            word = item[0]
            freq = item[1]
            preword =word[:premaxlen]
            add_to_vocab_multi(preword,rawprevocab,freq)
            add_to_vocab_multi_reverse(word[::-1],rawpostvocab,postmaxlen,minrootlen,freq)
#    funique = len(rawprevocab)
#    runique = len(rawpostvocab)
    prevfreq = -1
    num = 0
    for item in sorted(rawprevocab.items(),key=lambda x: x[1],reverse=True):
        word = item[0]
        freq = item[1]
        if freqnotrank:
            num = freq
        else:
            if freq!=prevfreq: num+=1
        add_to_codetree_terminal(word,rawprecodetree,num)
        if not loadrawfile and rawprefixfile:
            rawprefixfile.write(" {0} {1}\n".format(word,num))
        prevfreq = freq
    prevfreq = -1
    num = 0
    for item in sorted(rawpostvocab.items(),key=lambda x: x[1],reverse=True):
        word = item[0]
        freq = item[1]
        if freqnotrank:
            num = freq
        else:
            if freq!=prevfreq: num+=1
#        if freq!=prevfreq: num+=1 # tmp not used
        add_to_codetree_terminal(word,rawpostcodetree,num)
        if not loadrawfile and rawpostfixfile:
            rawpostfixfile.write(" {0} {1}\n".format(word,num))
        prevfreq = freq
        
#    print("vocab",len(vocab))
#    print("funique",funique)
#    print("runique",runique)
    if vocabout is not None:
        save_vocabulary(vocabout,vocab,True)
    return rawprecodetree,rawpostcodetree,vocab,rawprevocab
        

def print_subwords(infile,codefile,n,reverse=False):
    ngrams = Counter()
    vocab = extract_vocabulary(infile)
    # register (left or right) n-grams
    for word in vocab.keys():
        if reverse:
            if len(word)>=n+1: # right without first
                ngrams[word[-n:]] += 1
        else:
            if len(word)>=n: # left
                ngrams[word[:n]] += 1
    # count and print (left or right) n-grams
    print(len(ngrams))
    for item in sorted(ngrams.items(),key=lambda x: x[1],reverse=True):
        codefile.write("{0} {1}\n".format(item[0],item[1]))
    
def add_subwords(codetree,tword,pos,subgraph):
    pos0 = pos
    while pos < len(tword):
        s = tword[pos]
        if s not in codetree:
            return
        else:
            if codetree[s][0]>0:
                posnext = pos + 1
                if posnext not in subgraph[pos0]:
                    subgraph[pos0][posnext] = 0
                subgraph[pos0][posnext] = max(subgraph[pos0][posnext],codetree[s][0])
            pos += 1
            codetree = codetree[s][1]

def add_subwords_reverse(codetree,tword,pos,subgraph):
    posright = pos
    while pos >= 2:
        s = tword[pos-1]
        if s not in codetree:
            return
        else:
            if codetree[s][0]>0:
                posleft = pos - 1
                if posright not in subgraph[posleft]:
                    subgraph[posleft][posright] = 0
                subgraph[posleft][posright] = max(subgraph[posleft][posright],codetree[s][0])
            pos -= 1
            codetree = codetree[s][1]

def create_subgraph(precodetree,postcodetree,tword):
    subgraph = [{} for i in range(len(tword))]
    for pos in range(0,len(subgraph)-1):
        add_subwords(precodetree,tword,pos,subgraph)
#    for pos in range(len(subgraph),0,-1):
#        add_subwords_reverse(postcodetree,tword,pos,subgraph)
    add_subwords_reverse(postcodetree,tword,len(subgraph),subgraph)
    return subgraph

def analyze_subgraph(subgraph,word,track="",pos=0,freq="",leng=0):
    if pos==len(word):
        if leng<=3:
            print(track,freq)
    else:
        if len(track)>0:
            track += "-"
            freq+=" "
        for nextpos in subgraph[pos]:
            nextfreq = subgraph[pos][nextpos]
            analyze_subgraph(subgraph,word,track+word[pos:nextpos],nextpos,freq+str(nextfreq),leng+1)
            
# === Generic heuristics BEGIN            
            
nonprefixes_dict = {}        
            
vowels=u"aāeēiīoōuū";
vowdict={}
for v in vowels:
    vowdict[v]=1
    
def containsvowel(word):
    for s in word:
        if s in vowdict: return True
    return False

def is_good_part_generic(part,word=''):
    return (
        part.isalpha()
        and part.islower()
        and containsvowel(part)
    )
            
# === Generic heuristics END

# === English specific heuristics BEGIN    

nonprefixes_en = ["non","un","im"]
nonprefixes_dict_en={}
for v in nonprefixes_en:
    nonprefixes_dict_en[v]=1
            
def is_good_root_en(part,word):
    return len(part)>2 and is_good_part_generic(part)

def is_good_postfix_en(part):
    if len(part)<=2:
        return is_good_ending_en(part) or part in ["ly"]
    elif len(part)>5:
        return False
    else:
        if part in ["ment","ling","ness"]: return True
        if not is_good_part_generic(part):
            return False
        if part[0] not in vowdict:
            return False
        return True

def is_good_ending_en(part):
    return part in ["s","ed","e","y","es","er","ies"]
    
def is_good_prefix_en(part):
    return is_good_part_generic(part)

# === English specific  heuristics END

# === Quechua specific heuristics BEGIN    

nonprefixes_qz = []
nonprefixes_dict_qz={}

common_suffixes_qz = [
               "cha", "chi", "chka", "chra", "chu", "chá", 
               "hina",
               "kama", "kta", "kuna", "ku"
               "lla"
               "m", "man", "manta", "mi", "mu",
               "na", "naku", "naya", "nchik", "nchis", "nku", "nnaq", "ntin",
               "p", "pa", "paq", "pas", "paya", "pi", "pis", "pti", "puni", "pura",
               "qa", "qti",
               "raq", "rayku", "ri", "rqa", "rqu", "sa", "sh", "sha", "shi", "si", "spa", "sqa"
               "ta", "taq", 
               "wan", 
               "ya", "ykacha", "yki", "ykichik", "ykichis", "yku", "yna", "yoq", "ysi", "yuq",
               "ña", "ñiqi"]

common_endings_qz = ["n", "q", "s"]

for v in nonprefixes_qz:
    nonprefixes_dict_qz[v]=1
            
def is_good_root_qz(part,word):
    if part in ["noqa", "qan", "pay"]: return True
    #if part[0].isupper(): return True # doesnt do anything rn
    return len(part)>3 and is_good_part_generic(part)

def is_good_postfix_qz(part):
    if len(part)<=7:
        return is_good_ending_qz(part)
    else:
        for suffix in common_suffixes_qz:
            if suffix in part:
                return True
        if containsvowel(part[0]): # test what happens if we dont have this
            return False
        if not is_good_part_generic(part):
            return False
        
        return True

def is_good_ending_qz(part):
    return part in common_suffixes_qz
    
def is_good_prefix_qz(part):
    return is_good_part_generic(part)

# === Quechua specific  heuristics END

# === Latvian specific heuristics BEGIN            
            
nonprefixes_lv = ["ne"]
nonprefixes_dict_lv={}
for v in nonprefixes_lv:
    nonprefixes_dict_lv[v]=1
            
vowels_not_o=u"aāeēiīōuūy";
vowdict_not_o={}
for v in vowels_not_o:
    vowdict_not_o[v]=1

badrootstart_lv = "cčjlļmnņr"    
badrootstart_dict_lv={}
for v in badrootstart_lv:
    badrootstart_dict_lv[v]=1
badrootend_lv = ["šs"]
badrootend_dict_lv={}
for v in badrootend_lv:
    badrootend_dict_lv[v]=1

def is_good_root_lv(root,word):
#    if len(root)<=2: return False
    if root[-1] in vowdict_not_o: return False
    if root[-1] == "o" and len(root)<4: return False
    if root[-2] in ['p','t'] and root[-1] not in ['l','r','j','n','t','s','o']: return False
    if len(root)==len(word) and len(root)<4: return False
    if root[1] not in vowdict and root[0] in badrootstart_dict_lv: return False
    if root[-2:] in badrootend_dict_lv: return False
    return is_good_part_generic(root)

def is_good_postfix_lv(part):
    if len(part)==1:
        if part in vowdict: return True
        elif part in ["t","s","š"]: return True
        else: return False
    else:
        if not is_good_part_generic(part):
            return False
        if part[-1] not in vowdict and part[-1] not in ["m","s","š","t"]: return False
        if len(part)==2:
             # postfixes of length 2 should contain vowel at position 0 (LATVIAN?)
            if part[0] not in vowdict or part[-1]=="o":
                return False
        else: # postfix length 3 or more
            if part=="sies": return True 
            if part=="ties": return True 
            if part[:3]=="šan": return True 
            if part[:3]=="nīc": return True 
            if part[:4]=="niek": return True 
            if part[:4]=="niec": return True 
            if part[:4]=="nieč": return True 
            if not containsvowel(part[0]):
                return False
    return True

def is_good_ending_lv(part):
    """ Is ending in Latvian, assuming it is good postfix
    """
    if len(part)>4: return False
    elif len(part)==4:
        if part in ["sies","ties"]: return True
    elif len(part)==3:
        if part in ["iem","ies","ais"]: return True
    elif len(part)==2:
        if part[-1]=="š": return False
        elif part[0] in vowdict and part[1] in vowdict:
            if part in ["ai","ie","ei"]: return True
            else: return False
        elif part in ["om","ūs","et","ut","ūt"]: return False
        else: return True
    else: # length = 1
        return True
    return False
    
def is_good_prefix_lv(part):
    return is_good_part_generic(part)

# === Latvian specific heuristics END

# === Indonesian specific heuristics BEGIN

nonprefixes_dict_id={}

common_prefixes_id = ["ber", "di", "ke", "me", "mem", "men", "meng", "menge", "meny", "pe", "pem", "pen", "peng", "penge", "peny", "per", "se", "ter", 
                      "antar", "para", "eka", "kau", "ku", "oto", "pasca"]
common_suffixes_id = ["an", "kan", "i", "lah", "kah", "nya",
                      "pun", "ku", "mu"]
            
def is_good_root_id(part,word):
    return len(part)>3 and is_good_part_generic(part)

def is_good_postfix_id(part):
    if len(part)<=3:
        return is_good_ending_id(part)
    elif len(part)>3:
        return False
    else:
        if not is_good_part_generic(part):
            return False
        return True

def is_good_ending_id(part):
    return part in common_suffixes_id
    
def is_good_prefix_id(part):
    if part in common_prefixes_id:
        return True
    if len(part)>5:
        return False
    return is_good_part_generic(part)

# === Indonesian specific heuristics END

# === Marathi specific heuristics BEGIN

common_prefixes_mr = ["अ", "अन", "चौ", "ना", "निर्", "वि"]
common_suffixes_mr = ["अट‎", "आऊ‎", "आर्थ‎", "आव‎", "ई‎", "ई‎", "ईल‎", "णूक‎", "णे‎", "बा‎"]
            
def is_good_root_mr(part,word):
    return len(part)>3 and is_good_part_generic(part)

def is_good_postfix_mr(part):
    if len(part) == 1:
        return is_good_ending_mr(part)
    elif len(part)>3:
        return False
    else:
        if not is_good_part_generic(part):
            return False
        return True

def is_good_ending_mr(part):
    return part in common_suffixes_mr
    
def is_good_prefix_mr(part):
    if part in common_prefixes_mr:
        return True
    if len(part)>3:
        return False
    return is_good_part_generic(part)

# === Marathi specific heuristics END

# === Irish specific heuristics BEGIN

nonprefixes_dict_ga = {}

common_prefixes_ga = ['ain' ,'an' ,'ard','ath','ban','breac','ceann','comh','dea','dearg','dé'
                    ,'di','do','droch','dú','for','gar','il','in','iar','íos','lán','leath','meán'
                    ,'mí','mion','neamh','oir','os','príomh','réamh','ró','sár','sean','so']

# all suffix types included
common_suffixes_ga = ['a','ach','acha','achán','achas','achd','acht','adh','adóir','agán','aí','aibh','aidhe'
                    ,'aigh','áil','aimid','aíonn','aire','áis','áit','alú','amhail','án','ann','anna','arcacht'
                    ,'as','blast','blastach','chruthach','cít','clast','da','dóir','e','each','éad','eadh','eán'
                    ,'eann','eas','éir','eog','eoir','fad','fadh','fagach','faidh','fead','fidh','fileach','fóbach'
                    ,'fón','ga','gamacht','gán','gin','gineach','gineacht','gineas','giniteach','giniúil','graf'
                    ,'grafaíoch','grafaíocht','í','iam','ibh','idhe','igh','im','imid','in','ín','íonn','is'
                    ,'ít','íteas','iú','lann','lathach','lathaí','lathas','leipteach','lit','méadar','méadracht'
                    ,'méir','mhadh','mhar','mid','morf','morfach','morfacht','na','nastacht','ne','nn'
                    ,'obach','ocsacht','óg','óideach','oidhe','óir','óis','óma','ós','paite'
                    ,'pat','patach','péine','pláise','pód','r','ra'
                    ,'radh','sa','san','scóp','scópacht','se','sean','sóch','stóm','ta','te','tha'
                    ,'the','tóime','tóir','traí','trófach','tróife','trópacht','ú','uidhe','úil'
                    ]

def is_good_root_ga(part,word):
    return len(part)>3 and is_good_part_generic(part)

def is_good_postfix_ga(part):
    if len(part)<=3:
        return is_good_ending_ga(part)
    elif len(part)>3:
        return False
    else:
        if not is_good_part_generic(part):
            return False
        return True

def is_good_ending_ga(part):
    return part in common_suffixes_ga
    
def is_good_prefix_ga(part):
    if part in common_prefixes_ga:
        return True
    if len(part)>5:
        return False
    return is_good_part_generic(part)

# === Irish specific heuristics END

def add_heuristics(lang=''):
    lang = lang.lower()
    global is_good_prefix
    global is_good_root
    global is_good_postfix
    global is_good_ending
    global nonprefixes_dict
    if lang=='lv':
        is_good_prefix = is_good_prefix_lv
        is_good_root = is_good_root_lv
        is_good_postfix = is_good_postfix_lv
        is_good_ending = is_good_ending_lv
        nonprefixes_dict = nonprefixes_dict_lv
    elif lang=='en':
        is_good_prefix = is_good_prefix_en
        is_good_root = is_good_root_en
        is_good_postfix = is_good_postfix_en
        is_good_ending = is_good_ending_en
        nonprefixes_dict = nonprefixes_dict_en
    elif lang=='qz':
        is_good_prefix = is_good_prefix_qz
        is_good_root = is_good_root_qz
        is_good_postfix = is_good_postfix_qz
        is_good_ending = is_good_ending_qz
        nonprefixes_dict = nonprefixes_dict_qz
    elif lang=='qz':
        is_good_prefix = is_good_prefix_qz
        is_good_root = is_good_root_qz
        is_good_postfix = is_good_postfix_qz
        is_good_ending = is_good_ending_qz
        nonprefixes_dict = nonprefixes_dict_qz
    elif lang=='id':
        is_good_prefix = is_good_prefix_id
        is_good_root = is_good_root_id
        is_good_postfix = is_good_postfix_id
        is_good_ending = is_good_ending_id
        nonprefixes_dict = nonprefixes_dict_id
    elif lang=='ga':
        is_good_prefix = is_good_prefix_ga
        is_good_root = is_good_root_ga
        is_good_postfix = is_good_postfix_ga
        is_good_ending = is_good_ending_ga
        nonprefixes_dict = nonprefixes_dict_ga
    elif lang=='mr':
        is_good_prefix = is_good_prefix_mr
        is_good_root = is_good_root_mr
        is_good_postfix = is_good_postfix_mr
        is_good_ending = is_good_ending_mr
        nonprefixes_dict = nonprefixes_dict_qz
    else:
        lang = 'unspecified'
        is_good_prefix = is_good_prefix_en
        is_good_root = is_good_root_en
        is_good_postfix = is_good_postfix_en
        is_good_ending = is_good_ending_en
        nonprefixes_dict = nonprefixes_dict_en
    sys.stderr.write('Heuristics: {0}\n'.format(lang))

def analyze_prefixes(prefsource,rootsource,vocab,rawprevocab,preffile=None,loadfile=False):
    """ Collect candidate prefixes
    """
    prefixes = Counter()
    if loadfile:
        if preffile is not None:
            for line in preffile:
                entry = line.split()
                prefixes[entry[0]] = int(entry[1])
    else:
#        TEST=0
#        CNT=0
        for prefix in goodprefixes:
            prefixes[prefix] = goodprefixes[prefix]
        preflen1 = minpreflen
        preflen2 = 4
        rootlen1 = 4
        rootlen2 = 7
        for item in vocab.items():
            word = item[0]
#            freq = item[1]
            preftree = prefsource
            for p in range(1,preflen2+1):
                if p+rootlen1>len(word): break
                ps = word[p-1]
                if ps not in preftree: break
                elif preftree[ps][0]>0 and p>=preflen1:
                    prefix = word[:p]
                    if is_good_prefix(prefix) and search_codetree(prefix,badprefixes)==0:
                        roottree = rootsource
                        for r in range(1,rootlen2+1):
                            pr = p+r
                            if pr>len(word): break
                            prs = word[pr-1]
                            if prs not in roottree: break
#                            elif not freqnotrank: # ranking
#                                if prefixes[prefix]==0 or roottree[prs][0]<prefixes[prefix]:
#                                    prefixes[prefix]=roottree[prs][0]
#                            elif roottree[prs][0]>0 and r>=rootlen1 and is_good_root(word[p:pr],word): # frequence
#                                prefixes[prefix]+=roottree[prs][0]
                            root=word[p:pr]
                            if r>=rootlen1 and roottree[prs][0]>0 and is_good_root(root,word):
                                prefixes[prefix]+=rawprevocab[root]
                            roottree = roottree[prs][1]
                preftree = preftree[ps][1]
        if preffile is not None:
            for item in sorted(prefixes.items(),key=lambda x: x[1],reverse=True):
                preffile.write(" {0} {1}\n".format(item[0],item[1]))
#        print("CNT",CNT,TEST)
    return prefixes
        
longenoughpplen = 5
ppregbase = 3

def analyze_postfixes(rootsource,postsource,vocab,rawprevocab,postfile=None,sufffile=None,endfile=None,loadfile=False):
    """ Collect candidate postfixes, suffixes, endings
    """
    postfixes = Counter()
    suffixes = Counter()
    endings = Counter()
    if loadfile:
        if postfile is not None:
            for line in postfile:
                entry = line.split()
                postfixes[entry[0]] = int(entry[1])
        if sufffile is not None:
            for line in sufffile:
                entry = line.split()
                suffixes[entry[0]] = int(entry[1])
        if endfile is not None:
            for line in endfile:
                entry = line.split()
                endings[entry[0]] = int(entry[1])
    else:
        for postfix in goodpostfixes:
            postfixes[postfix] = goodpostfixes[postfix]
        postlen2 = 7
        rootlen1 = 4
        rootlen2 = 7
        for item in vocab.items():
            word = item[0]
#            freq = item[1]
            posttree = postsource
            for p in range(1,postlen2+1):
                if p+rootlen1>len(word): break
                ps = word[-p]
                if ps not in posttree: break
                elif posttree[ps][0]>0:
                    postfix = word[-p:]
                    if is_good_postfix(postfix) and search_codetree(postfix,badpostfixes)==0:
                        for rootlen in range(rootlen1,1+min(rootlen2,len(word)-p)):
                            roottree = rootsource
                            for r in range(rootlen,0,-1):
                                pr = p+r
                                prs = word[-pr]
                                if prs not in roottree: break
#                                elif not freqnotrank: # ranking
#                                    if postfixes[postfix]==0 or roottree[prs][0]<postfixes[postfix]:
#                                        postfixes[postfix]=roottree[prs][0]
#                                        if is_good_ending(postfix):
#                                            if endings[postfix]==0 or roottree[prs][0]<endings[postfix]:
#                                                endings[postfix]+=roottree[prs][0]
#                                elif roottree[prs][0]>0 and r==1 and is_good_root(word[-p-rootlen:-p],word): # frequence
#                                    postfixes[postfix]+=roottree[prs][0]
#                                    if is_good_ending(postfix):
#                                        endings[postfix]+=roottree[prs][0]
                                root=word[-p-rootlen:-p]
                                if r==1 and roottree[prs][0]>0 and is_good_root(root,word): # frequence
                                    postfixes[postfix]+=rawprevocab[root]
                                    if is_good_ending(postfix):
                                        endings[postfix]+=rawprevocab[root]
                                roottree = roottree[prs][1]
                posttree = posttree[ps][1]
        minsufflen = 1
        # extract suffixes
        for postfix in postfixes:
            for pos in range(minsufflen,len(postfix)-1):
                suffix=postfix[:pos]
                ending=postfix[pos:]
                if endings[ending]>0:
                    suffixes[suffix]+=postfixes[postfix]
        # regularize weight
        for postfix in postfixes:
            if len(postfix)<longenoughpplen: # longer ppfixes are better
                expo = longenoughpplen - len(postfix)
                postfixes[postfix] = postfixes[postfix] // round(ppregbase**expo)
        for suffix in suffixes:
            if len(suffix)<longenoughpplen: # longer ppfixes are better
                expo = longenoughpplen - len(suffix)
                suffixes[suffix] = suffixes[suffix] // round(ppregbase**expo)
        # print to files
        if postfile is not None:
            for item in sorted(postfixes.items(),key=lambda x: x[1],reverse=True):
                postfile.write(" {0} {1}\n".format(item[0],item[1]))
        if sufffile is not None:
            for item in sorted(suffixes.items(),key=lambda x: x[1],reverse=True):
                sufffile.write(" {0} {1}\n".format(item[0],item[1]))
        if endfile is not None:
            for item in sorted(endings.items(),key=lambda x: x[1],reverse=True):
                endfile.write(" {0} {1}\n".format(item[0],item[1]))
    return postfixes,suffixes,endings

def explore_codetree_plus(codetree,tword,wordpos0=0,emptysubword=False):
    store={}
    if emptysubword:
        store[0]=0 # for empty subword
    wlen = len(tword)
    for wordpos in range(wordpos0,wlen):
        s = tword[wordpos]
        if s not in codetree:
            break
        val = codetree[s][0]    
        if val>0:
            pos = wordpos-wordpos0+1
            store[pos]=val
        codetree = codetree[s][1]
    return store

def extend_subword_matrix(dest,src,addempty=False):
    for dpos in range(len(dest)):
        ddict=deepcopy(dest[dpos])
        for ditem in ddict.items():
            dlen=ditem[0]
            drank=ditem[1]
            spos = dlen+dpos
            if spos<len(src):
                for sitem in src[spos].items():
                    slen=sitem[0]
                    srank=sitem[1]
                    rank=max(drank,srank)
                    dslen=dlen+slen
                    if dslen not in dest[dpos]:
                        dest[dpos][dslen]=rank
                    elif rank<dest[dpos][dslen]:
                        dest[dpos][dslen]=rank
        if addempty:
            dest[dpos][0]=0

def merge_subword_matrix(dest,src,addempty=False):
    for dpos in range(len(dest)):
        for sitem in src[dpos].items():
            slen=sitem[0]
            srank=sitem[1]
            if slen not in dest[dpos]:
                dest[dpos][slen]=srank
            elif srank<dest[dpos][slen]:
                dest[dpos][slen]=srank
        if addempty:
            dest[dpos][0]=0

def reverse_subword_matrix(mx,emptysubword=True):
    mlen = len(mx)
    if emptysubword:
        rmx = [{0:0} for i in range(mlen)]
    else:
        rmx = [{} for i in range(mlen)]
    for pos in range(mlen):
        seq = mx[pos]
        for seqel in seq.items():
            sublen=seqel[0]
            subrate=seqel[1]
            lastpos = pos+sublen-1
            pos2 = mlen-lastpos-1
            rmx[pos2][sublen]=subrate
#            rmx[pos2].append((sublen,subrate))
    return rmx

def build_codetree_best(ppvocab,rate,reverse,datafile=None,loadfile=False):
    """ Collect best prefixes (reverse=False) or postfixes (reverse=True)
    """
    if loadfile:
        codetree = read_codetree(datafile,reverse)
    else:
        codetree = {}
        icount = len(ppvocab.items())
        if rate>1.0: bestcount=int(rate)
        else: bestcount = int(round(icount * rate))
        prevfreq = 0
        numx = 0
        num = 0
        for item in sorted(ppvocab.items(),key=lambda x: x[1],reverse=True):
            if numx>=bestcount: break
            freq = int(item[1])
            if freq!=prevfreq: num+=1
            word = item[0]
            numout = num    
            if datafile is not None:
                datafile.write(u" {0} {1}\n".format(word,numout))
            if reverse: word=word[::-1]
            add_to_codetree_terminal(word,codetree,numout)
            prevfreq = freq
            numx += 1
    return codetree

def extract_root(precodetree,bestprecodetree,bestpostcodetree,word,minrootlen,bestcount):
    # create candidate list of prefixes, with a prefix denoted as its length
    prestore = explore_codetree_plus(bestprecodetree,word,0,True)
    # create candidate list of postfixes, with a postfix denoted as its length
    poststore = explore_codetree_plus(bestpostcodetree,word[::-1],0,True)
    roots = Counter()
    wlen = len(word)
    for xpos in prestore.items(): # all available prefixes
        pos = xpos[0]
        for ypos in poststore.items(): # all available postfixes
            pos2rev = ypos[0]
            if pos+pos2rev+minrootlen<=wlen:
                pos2 = wlen-pos2rev
                root=word[pos:pos2]
#                postfix = word[pos2:]
                if (search_codetree(root,precodetree)>0
                    and is_good_root(root,word)
                    and search_codetree(root,badroots)==0
                    ):
                    prerank=xpos[1]
#                    if pos>0:
#                        if verbose:
#                            print("{1}({0})".format(prerank,word[:pos]),end=" ")
                    rootrank = search_codetree(root,precodetree)
#                    if verbose:
#                        print("{1}[{0}]".format(rootrank,root),end=" ")
                    postrank=ypos[1]
#                    if pos2rev>0:
#                        if verbose:
#                            print("{1}({0})".format(postrank,postfix),end=" ")
#                    if freqnotrank:
#                        rootrate = rootrank-prerank-postrank
#                    else:
                    rootrate = prerank+rootrank+postrank
#                    rootrate = rootrank #+prerank+postrank
                    roots[root]=rootrate
#                    if verbose:
#                        print("+{0}".format(rootrate))
    minroots=[]
    if len(roots)>0:
        cnt=0
        for root in sorted(roots,key=lambda x: roots[x]):
#            if root=="eirop":
#                print("rootx",roots[root])
            minroots.append(root)
            cnt+=1
            if cnt>=bestcount: break
#        minroot=min(roots,key=lambda x: roots[x])
    return minroots #,roots[minroot]
    
longenoughrootlen = 5
rootregbase = 4
minrootfreq = 2

def collect_roots(vocab,rawprecodetree,bestprecodetree,bestpostcodetree,datafile=None,loadfile=False,bestcount=1):
    if loadfile:
        roottree = read_codetree(datafile)
    else:
        roottree = {}
        roots = Counter()
        for root in goodroots:
            roots[root] = goodroots[root]
        for word in vocab:
            minroots = extract_root(rawprecodetree,bestprecodetree,bestpostcodetree,word,minrootlen,bestcount)
            cnt=0
            for root in minroots:
                freq = search_codetree(word,rawprecodetree)
                if freq>0:
                    roots[root] += vocab[word]
                cnt+=1
        for root in roots:
            if len(root)<longenoughrootlen: # longer roots are better
                expo = longenoughrootlen - len(root)
                roots[root] = roots[root] // round(rootregbase**expo)
        prevfreq = 0
        numx = 0
        num = 0
        for root in sorted(roots,key=lambda x: roots[x], reverse=True):
            freq = roots[root]
            if freq<minrootfreq: break
            if freq!=prevfreq: num+=1
            if datafile:
                datafile.write(u" {0} {1}\n".format(root,num))
            add_to_codetree_terminal(root,roottree,num)
            numx += 1
            prevfreq = freq
#        print("roots",numx)
    return roottree
                
rootfactor = 1
rootblockweight = 1000000

# status: 0-prefix, 1-root, 2-postfix, 3-endings
def segment_word0(mxx,word,pos,step,status,track,trackweight,trackstore,trackweightstore):
    if pos>=len(mxx[status]): return # finished after prefix
#    print(pos,step,status,len(track))
#    print("SPV",status,pos,mxx[status][pos])
    wordlen=len(word)
    for candidate in mxx[status][pos].items():
        pos2 = pos + candidate[0]
        if status==1: # root
            trackweight2 = trackweight + candidate[1] * rootfactor
        else:
            trackweight2 = trackweight + candidate[1]
        if step==len(track):
            track.append([pos2,candidate[1]])
        else:
            track[step] = [pos2,candidate[1]]
        if status<=1: # prefix or root
            segment_word0(mxx,word,pos2,step+1,(status+1)%3,track,trackweight2,trackstore,trackweightstore)
        else: # post
            if pos2==wordlen:
                tracktostore = list(track[:step+1])
                trackstore.append(tracktostore)
                trackweightstore.append(trackweight2+len(tracktostore)*rootblockweight//3)
#                print("added",tracktostore)
            else:
                segment_word0(mxx,word,pos2,step+1,(status+1)%3,track,trackweight2,trackstore,trackweightstore)

maxgerootlen = 9
def obtain_segment_track(bestprecodetree,roottree,bestsuffcodetree,bestpostcodetree,bestendcodetree,bestvocab,word,generateroots=True,verbose=False):
    """ Collect list of segmentation tracks, each in form (prefix, root, postfix)+ and compute weights (the less, the better)
        and return the best one
    """
    if word in bestvocab or len (word)>20:
        return []
    prematrix = []
#    print("len-bestprecodetree",len(bestprecodetree))
#    print(bestprecodetree)
    for pos in range(len(word)):
        prematrix.append(
                explore_codetree_plus(bestprecodetree,word,pos)
                )
    pre2 = deepcopy(prematrix)
    extend_subword_matrix(prematrix,pre2,True)
    if verbose:
        sys.stdout.write("PRE\n")
        for pos in range(len(prematrix)):
            sys.stdout.write("{0} {1} {2}\n".format(pos,word[pos],prematrix[pos]))
#            print(pos,word[pos],prematrix[pos])

    rootmatrix = []

    for pos in range(len(word)):
        rootmatrix.append(
                explore_codetree_plus(roottree,word,pos)
                )

    if verbose:
        sys.stdout.write("ROOT\n")
        for pos in range(len(rootmatrix)):
            sys.stdout.write("{0} {1} {2}\n".format(pos,word[pos],rootmatrix[pos]))

    endmatrix0 = []
    postmatrix0 = []
    suffmatrix0 = []
    for pos in range(len(word)):
        endmatrix0.append(
                explore_codetree_plus(bestendcodetree,word[::-1],pos)
                )
#        postmatrix0.append(
#                explore_codetree_plus(bestpostcodetree,word[::-1],pos)
#                )
        suffmatrix0.append(
                explore_codetree_plus(bestsuffcodetree,word[::-1],pos)
                )
    if verbose:
        sys.stdout.write("POST00\n")
        for pos in range(len(postmatrix0)):
            sys.stdout.write("{0} {1} {2}\n".format(pos,word[::-1][pos],postmatrix0[pos]))
        sys.stdout.write("SUFF00\n")
        for pos in range(len(suffmatrix0)):
            sys.stdout.write("{0} {1} {2}\n".format(pos,word[::-1][pos],suffmatrix0[pos]))

#    endmatrix = reverse_subword_matrix(postmatrix0,True) # without suffixes
#    endmatrix.append({0:0})

#    extend_subword_matrix(postmatrix0,suffmatrix0,False)
#    merge_subword_matrix(postmatrix0,suffmatrix0,False)

    extend_subword_matrix(endmatrix0,suffmatrix0,False)
    merge_subword_matrix(endmatrix0,suffmatrix0,False)
    postmatrix0 = endmatrix0

    if verbose:
        sys.stdout.write("POST0\n")
        for pos in range(len(postmatrix0)):
            sys.stdout.write("{0} {1} {2}\n".format(pos,word[::-1][pos],postmatrix0[pos]))
    postmatrix = reverse_subword_matrix(postmatrix0,True)
    postmatrix.append({0:0})
    if verbose:
        sys.stdout.write("POST\n")
        for pos in range(len(postmatrix)):
            wordplus=word+" "
            sys.stdout.write("{0} {1} {2}\n".format(pos,wordplus[pos],postmatrix[pos]))
    track = [[0,0] for i in range(len(word)*2)]
    trackweight = 0
    trackstore = []
    trackweightstore = []
#    mxx = [prematrix,rootmatrix,postmatrix,endmatrix]
    mxx = [prematrix,rootmatrix,postmatrix]
    segment_word0(mxx,word,pos=0,step=0,status=0,track=track,
                  trackweight=trackweight,trackstore=trackstore,trackweightstore=trackweightstore)
    
    # unable to find track from available roots
    if len(trackweightstore)==0:
        if generateroots:
            for pos in range(len(word)):
                for candidatelen in range(2,min(maxgerootlen,len(word)-pos)+1):
                    candidateroot=word[pos:pos+candidatelen]
                    if is_good_root(candidateroot,word):
                        rootrank = search_codetree(candidateroot,roottree)
                        if rootrank>0:
                            rootmatrix[pos][candidatelen]=rootrank
                        else:
                            # x*candidatelen...: more letters generated roots make rank worse
                            # candidatelen+1: more generated roots make rank worse
                            # (one generated root of length 2n is better than two of lengths 4 each)
                            rootmatrix[pos][candidatelen]=rootblockweight*(candidatelen+1)
            if verbose:
                sys.stdout.write("ROOT2\n")
                for pos in range(len(rootmatrix)):
                    sys.stdout.write("{0} {1} {2}\n".format(pos,word[pos],rootmatrix[pos]))
            segment_word0(mxx,word,pos=0,step=0,status=0,track=track,
                          trackweight=trackweight,trackstore=trackstore,trackweightstore=trackweightstore)
        else: # do not generate roots, take only postfix
            lastx = postmatrix0[0]
            if len(lastx)>0:
                bestlist = sorted(lastx.keys(),key=lambda x: lastx[x])
                for i in range(len(bestlist)):
                    best=bestlist[i]
                    bestweight=lastx[best]
                    if len(word[:-best])>=minrootlen and is_good_root(word[:-best],word):
                        track=[[0,0],[len(word)-best,bestweight],[len(word),0]]
                        trackstore.append(track)
                        trackweightstore.append(bestweight)
                        break
    if verbose:
        num=0
        for t in trackstore:
            sys.stdout.write("{0} {1} {2}\n".format(num,trackweightstore[num],t))
            num+=1
        sys.stdout.write("{0}\n".format(trackweightstore))

    if len(trackweightstore)==0: return []
    else:
        if verbose:
            sys.stdout.write("{0}\n".format(argmin(trackweightstore)))
            sys.stdout.write("{0}\n".format(trackstore[argmin(trackweightstore)]))
        return trackstore[argmin(trackweightstore)]

def mark_alpha_segmentation(roottree,bestvocab,track,word,marker1,mode,optmode=1):
    """ Generate segmented word given track
    """
    if len(track)==0: # no track built
        if mode==3:
            segmentlist=[word+marker1]
        else:
            segmentlist=[word]
    else:
        wordpos=0
        segmentlist = []
        status = 0 # 0-prefix, 1-root, 2-postfix
        t = 0
        while t < len(track):
#            trackpos = track[t]
            wordposx = track[t][0]
            if status==0: # PRP optimization
                wordposy = track[t+1][0]
                wordposz = track[t+2][0]
                if optmode==0:
                    pass
                elif optmode==1:
                    segmenty = word[wordpos:wordposy] # prefix+root
                    segmentxyz = word[wordpos:wordposz] # p+r+p
                    segmentyz = word[wordposx:wordposz] # r+p
                    if segmentxyz in bestvocab and word[wordpos:wordposx] not in nonprefixes_dict:
                        # concatenate prefix+root+postfix, reduces amount of segments
                        if t+3<len(track) or mode>0:
                            track[t][0]=wordpos
                            track[t+1][0]=wordposz
                            track[t+2][0]=wordposz
                    elif wordposz>wordposy and segmentyz in bestvocab:
                        # concatenate root+postfix, reduces amount of segments
                        if t+3<len(track) or mode>0:
                            track[t+1][0]=wordposz
                    elif wordposx>wordpos and search_codetree(segmenty,roottree)>0: # prefix+root is among roots
                        track[t][0]=wordpos
#                        track[t+1][0]=wordposy # prefix added to root
                    elif track[t+1][1]>rootblockweight and t+3<len(track):
                        # generated roots (not in last position) concatenated
                        # with its prefix and postfix, reduces amount of segments
                        if word[wordpos:wordposx] not in nonprefixes_dict:
                            track[t][0]=wordpos
                        track[t+1][0]=wordposz
#                        track[t+2][0]=wordposz
                elif optmode==2:
                    if t+3<len(track):
                        # roots (NOT in last prp position) concatenated
                        # with its prefix and postfix, reduces amount of segments
                        if word[wordpos:wordposx] not in nonprefixes_dict:
                            track[t][0]=wordpos
                        track[t+1][0]=wordposz
#                        track[t+2][0]=wordposz
                    else:
                        # roots (in last prp position) concatenated
                        # with its prefix (not postfix), reduces amount of segments
#                        wordposz = track[t+2][0]
                        if word[wordpos:wordposx] not in nonprefixes_dict:
                            track[t][0]=wordpos
#                        track[t+1][0]=wordposy
#                        track[t+2][0]=wordposz
            wordpos2 = track[t][0]
            if wordpos2>wordpos:
                segment = word[wordpos:wordpos2]
                if mode==0:
                    segmentlist.append(segment)
                elif mode==1:
                    if status==0: #prefix marked
                        segmentlist.append(segment+marker1)
                    elif status==1:
                        segmentlist.append(segment)
                        wordpos3 = track[t+1][0]
                        isprelast = (t==len(track)-2)
                        # if the root is not the last root and no postfix follows
                        if not isprelast and wordpos3-wordpos2==0:
                            segmentlist.append(marker1)
                    elif status==2:
                        segmentlist.append(marker1+segment)
                        islast = (t==len(track)-1)
                        if not islast:
                            segmentlist.append(marker1)
                elif mode==2:
                    if status==0: #prefix marked
                        segmentlist.append(segment+marker1)
                    elif status==1:
                        segmentlist.append(segment)
                    elif status==2:
                        segmentlist.append(marker1+segment)
                elif mode==3:
                    segmentlist.append(segment+marker1)
                            
            wordpos = wordpos2
            status = (status+1)%3
            t+=1
    return segmentlist

def segment_word(bestprecodetree,roottree,bestsuffcodetree,bestpostcodetree,bestendcodetree,bestvocab,word,marker1,marker2,mode,generateroots=False,optmode=1,verbose=False):
    """ Preprocess string before segmentation into list of alpha(letters) and non-alpha parts,
        alpha parts are then prp segmented, and then segmented word put together with segmentation marks,
        considering also uppercase/lowercase processing
        mode=0: marker1 denotes end of word
        mode=1: marker1 denotes prefix/postfix and link
        mode=2: marker1 denotes prefix/postfix and begin/end
        mode=3: marker1 denotes link to next segment (like in BPE)
        mode+100: no uppercase processing (marker2 denotes uppercase for the first letter of the following segment)
    """
    segmentlist = []
    pos0 = 0
    prevalpha = False
    endsbyroot = False
    AlphaProcessed = True
    uppercasemode = mode<100
    mode %= 100
#    startmarked = False
#    upperstartmarked = False
    if word in bestvocab:
        segmentlist.append(word)
    else:
        for pos in range(len(word)+1): # symbol by symbol processing; takes one position afre end to process last segment
            if pos<len(word):
                alpha = word[pos].isalpha()
            if pos==len(word) or pos > 0 and alpha != prevalpha: # boundary of alpha/nonalpha parts
                subword=word[pos0:pos]
                subwordplus=subword
                if prevalpha: # process alpha part
                    if pos0>0: # if alpha part follows non-alpha part, the non-alpha part marked
                        if mode==0: segmentlist[-1] += marker1
                        elif mode==1: segmentlist.append(marker1)
                    AlphaProcessed = False
                    if isUlower(subword):
                        subwordplus = subwordplus.lower()
                        if uppercasemode:
                            segmentlist.append(marker2)
                            subword = subwordplus
    #                    if startmarked or mode<=1:
    #                        segmentlist.append(marker2)
    #                    else:
    #                        segmentlist.append(marker2+marker1)
    #                        upperstartmarked = True
    #                        startmarked = True
                    track = obtain_segment_track(bestprecodetree,roottree,bestsuffcodetree,bestpostcodetree,bestendcodetree,bestvocab,subwordplus,generateroots,verbose)
                    if verbose:
                        sys.stdout.write("TRACK {0}\n".format(track))
                    if mode==0:
                        if len(track)==0: endsbyroot=False
                        elif track[-1][0]==track[-2][0]: # empty postfixpart
                             # only root of length <=3 (thus considered to be small word without marker as separate segment)
                            # (empty prefix and root length <=5) 
                            if len(track)==3 and track[-3][0]==0 and track[-2][0]-track[-3][0]<=5:
                                endsbyroot=False
                            else:
                                endsbyroot=True
                        else: endsbyroot=False
                    segmentlist+=mark_alpha_segmentation(roottree,bestvocab,track,subword,marker1,mode,optmode)
                    islast = (pos==len(word))
                    if islast and mode==0:
                        if endsbyroot: # marker set after word as separate segment
                            segmentlist += marker1
                            AlphaProcessed = True
                        else:
                            segmentlist[-1] = marker1 + segmentlist[-1] # postfix or small word marked (marker before it as part of it)
                            AlphaProcessed = True
    
                else: # process non alpha part -- no segmentation performed -- forwarded to BPE
                    if not AlphaProcessed:
                        AlphaProcessed = True
                        if mode==0: subword = marker1 + subword
                        elif mode==1: segmentlist.append(marker1)
                    if mode==3: subword += marker1
                    segmentlist.append(subword)
                    endsbyroot = False
                pos0 = pos
            prevalpha = alpha
    if mode==2: # postprocessing with begin/end
        len1=len(marker1)
        if len(segmentlist)==1: # single segment: do nothing
            pass
        elif len(segmentlist)==2 and segmentlist[0]==marker2: # single segment preceeded by uppercase mark: do nothing
            pass
        elif len(segmentlist)==2 and segmentlist[-1][:len1]==marker1: # two segments ended by postfix
            segmentlist[-1] = marker1 + segmentlist[-1]
        # the same with uppercase mark
        elif len(segmentlist)==3 and segmentlist[0]==marker2 and segmentlist[-1][:len1]==marker1:
            segmentlist[-1] = marker1 + segmentlist[-1]
        else: # to put begin and end marks
            # BEGINNING
            # if uppercase mark or prefix in the beginning: add marker to it
            if segmentlist[0]==marker2 or segmentlist[0][-len1:]==marker1:
                segmentlist[0]+=marker1
            else: # otherwise add extra marker
                segmentlist.insert(0,marker1)
            # END
            # if postfix in the end: add marker to it
            if segmentlist[-1][:len1]==marker1:
                segmentlist[-1] = marker1 + segmentlist[-1]
            else: # otherwise add extra marker
                segmentlist.append(marker1+marker1)
    elif mode==3:
        len1=len(marker1)
        if segmentlist[-1][-len1:]==marker1:
            segmentlist[-1] = segmentlist[-1][:-len1]
    return segmentlist
    
def learn_prpe(infile,outfilepref,outfileroot,outfilesuff,outfilepost,outfileend,outfilebestvocab,ratepref=20,ratesuff=400,ratepost=0.1,ratevocab=10000,
              ingoodpref=None,inbadpref=None,ingoodroot=None,inbadroot=None,ingoodpost=None,inbadpost=None,iterations=1,lang='lv'):
    """learn PRP encoding - raw prefixes, prefixes, roots, suffixes, postfixes, endings
    """
    global goodprefixes
    global badprefixes
    global goodroots
    global badroots
    global goodpostfixes
    global badpostfixes
    if ingoodpref is not None: goodprefixes = read_vocabulary(ingoodpref)
    if inbadpref is not None: badprefixes = read_codetree(inbadpref)
    if ingoodroot is not None: goodroots = read_vocabulary(ingoodroot)
    if inbadroot is not None: badroots = read_codetree(inbadroot)
    if ingoodpost is not None: goodpostfixes = read_vocabulary(ingoodpost)
    if inbadpost is not None: badpostfixes = read_codetree(inbadpost)
    
    bestprecodetree = None
    roottree = None
    bestpostcodetree = None

    add_heuristics(lang)

    rawprecodetree,rawpostcodetree,vocab,rawprevocab=register_subwords(infile,premaxlen,postmaxlen,minrootlen)

    # PRP extraction
    mainprefrate = 0.05
    mainpostrate = 0.05

    suffrate = ratesuff
    lastpostrate = ratepost
    lastprefrate = ratepref
    iters = iterations
    save_vocabulary(outfilebestvocab,vocab,order=True,reverseorder=True,alphaonly=False,
                    maxcount=ratevocab)
#    save_vocabulary(outfilebestvocab,vocab,True,True,True,ratevocab)
    for it in range(iters):
        # first processing
        if it==0: # first
            prefsource = rawprecodetree
            rootsource = rawprecodetree
            postsource = rawpostcodetree
        else: # not first
            prefsource = bestprecodetree
            rootsource = roottree
            postsource = bestpostcodetree


#                postrate = mainpostrate
        if it<iters-1: # not last
            prefout = None
            postout = None
            suffout= None
            endout = None
            prefrate = mainprefrate**(1/(iters-it))
            postrate = mainpostrate**(1/(iters-it))
            bestprefout = None
            bestsuffout = None
            bestendout = None
            bestpostout = None
            rootout = None
        else: # last
            prefout = None
            postout = None
            suffout= None
            endout = None
            prefrate = lastprefrate
            postrate = lastpostrate
            bestprefout = outfilepref
            rootout = outfileroot
            bestsuffout = outfilesuff
            bestendout = outfileend
            bestpostout = outfilepost
        
        # second processing
        prevocab = analyze_prefixes(prefsource,rootsource,vocab,rawprevocab,prefout,loadfile=False)
        postvocab,suffvocab,endvocab = analyze_postfixes(rootsource,postsource,vocab,rawprevocab,postout,suffout,endout,loadfile=False)
        
        bestprecodetree = build_codetree_best(prevocab,rate=prefrate,reverse=False,datafile=bestprefout,loadfile=False)
        bestpostcodetree = build_codetree_best(postvocab,rate=postrate,reverse=True,datafile=bestpostout,loadfile=False)
        roottree=collect_roots(vocab,rawprecodetree,bestprecodetree,bestpostcodetree,rootout,loadfile=False,bestcount=1)

    build_codetree_best(suffvocab,rate=suffrate,reverse=True,datafile=bestsuffout,loadfile=False)
    build_codetree_best(endvocab,rate=1.0,reverse=True,datafile=bestendout,loadfile=False)

def segment_sentence(bestprecodetree,roottree,bestsuffcodetree,bestpostcodetree,bestendcodetree,bestvocab,sentence,marker1,marker2,mode=0,generateroots=False,optmode=1,verbose=False):
    """segment line of words (whitespace-tokenized string) with PRP encoding
    """
    output = []
    for word in sentence.split():
#        word = processMeta(word)
        segmented = segment_word(bestprecodetree,roottree,bestsuffcodetree,bestpostcodetree,bestendcodetree,bestvocab,word,marker1,marker2,mode,generateroots,optmode,verbose)
        if mode%100==2: # optimizing usage of begin/end markers (omitting end marker, if begin marker follows)
            if len(output)>0 and output[-1]==marker1+marker1: # previous word ended by separate endmarker
                if segmented[0]==marker1: # current word starts by marker
                    del output[-1]
                if segmented[0][-len(marker1)*2:]==marker1+marker1: # current word starts by prefix marked as beginning
                    del output[-1]
        output += segmented
    return ' '.join(output)

# code 9474: '│'; code 9553: '║'
def apply_prpe(infile,outfile,infilepref,infileroot,infilesuff,infilepost,infileend,infilebestvocab,marker1="9474",marker2="9553",bigmode=1,generateroots=False,lang='lv'):
    """segment input stream with PRP encoding
    """
    if sys.version_info < (3, 0):
        if marker1.isdigit(): marker1 = unichr(int(marker1))
        if marker2.isdigit(): marker2 = unichr(int(marker2))
    else:
        if marker1 == '0': marker1 = ""
        if marker2 == '0': marker2 = ""
        if marker1.isdigit(): marker1 = chr(int(marker1))
        if marker2.isdigit(): marker2 = chr(int(marker2))

    add_heuristics(lang)
    
    optmode = bigmode // 1000
    mode = bigmode % 1000

    bestprecodetree = read_codetree(infilepref,reverse=False)
    bestsuffcodetree = read_codetree(infilesuff,reverse=True)
    bestpostcodetree = read_codetree(infilepost,reverse=True)
    bestendcodetree = read_codetree(infileend,reverse=True)
    roottree = read_codetree(infileroot)
    bestvocab = read_vocabulary(infilebestvocab,reverse=False)
    for sentence in infile:
        outfile.write(segment_sentence(bestprecodetree,roottree,bestsuffcodetree,bestpostcodetree,bestendcodetree,bestvocab,sentence,marker1=marker1,marker2=marker2,mode=mode,generateroots=generateroots,optmode=optmode).strip())
        outfile.write(' \n')

def unprocess_line_prpe(sentence,marker1,marker2,mode):
    output = []
    len1 = len(marker1)
    len2 = len(marker2)
    upper = False
    marked = False
    markednext = False
    wordstarted = False
    mode %= 100
    for word in sentence.split():
        # uppercase marking
        if word==marker2:
            upper=True
            continue
        elif mode==2 and word[:len2]==marker2: # in mode=2
            upper=True
            word = word[len2:]
        elif upper:
            word = word[0].upper() + word[1:]
            upper = False
        if mode==0:
            # determine connection to previous segment
            if word==marker1:
                marked = False
                continue
            elif word[:len1]==marker1 and not word[len1].isalpha():
                word = word[len1:]
                marked = True
            elif word[:len1]==marker1:
                word = word[len1:]
                markednext = False
            elif word.isalpha():
                markednext = True
            if word[-len1:]==marker1 and not word[len1].isalpha():
                word = word[:-len1]
                markednext = True
            # add segment
            if marked:
                output[-1]+=word
                marked = False
            else:
                output.append(word)
            # determine connection to next segment
            if markednext:
                markednext = False
                marked = True
        elif mode==1:
            # determine connection to previous segment
            if word==marker1:
                marked = True
                continue
            elif word[:len1]==marker1:
                marked = True
                word = word[len1:]
            # add segment
            if marked:
                output[-1]+=word
                marked = False
            else:
                output.append(word)
            # determine connection to next segment
            if output[-1][-len1:]==marker1:
                marked = True
                output[-1] = output[-1][:-len1]
        elif mode==2:
            if word==marker1: # beginning as separate marker
                wordstarted = True
                output.append('')
            elif word==marker1+marker1: # end as separate marker
                wordstarted = False
            elif word[-len1*2:]==marker1+marker1: # beginning as prefix
                wordstarted = True
                output.append(word[:-len1*2])
            elif word[:len1*2]==marker1+marker1: # end as postfix
                wordstarted = False
                output[-1]+=word[len1*2:]
            else:
                if word[-len1:]==marker1: # prefix
                    word = word[:-len1]
                elif word[:len1]==marker1: # postfix
                    word = word[len1:]
                if wordstarted:
                    output[-1]+=word
                else:
                    output.append(word)
        elif mode==3:
            if marked:
                output[-1]+=word
            else:
                output.append(word)
            marked = False
            if output[-1][-len1:]==marker1:
                output[-1]=output[-1][:-len1]
                marked = True
            
    return ' '.join(output)

# code 9474: '│'; code 9553: '║'
def unprocess_prpe(infile,outfile,marker1="9474",marker2="9553",mode=1):
    if sys.version_info < (3, 0):
        if marker1.isdigit(): marker1 = unichr(int(marker1))
        if marker2.isdigit(): marker2 = unichr(int(marker2))
    else:
        if marker1.isdigit(): marker1 = chr(int(marker1))
        if marker2.isdigit(): marker2 = chr(int(marker2))
    for line in infile:
        outfile.write(unprocess_line_prpe(line,marker1,marker2,mode).strip())
        outfile.write(' \n')
