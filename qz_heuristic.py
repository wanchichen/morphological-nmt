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
    return len(part)>3 and is_good_part_generic(part)

def is_good_postfix_qz(part):
    if len(part)<=7:
        return is_good_ending_qz(part)
    else:
        for suffix in common_suffixes_qz:
            if suffix in part:
                return True
        if containsvowel(part[0]):
            return False
        if not is_good_part_generic(part):
            return False
        
        return True

def is_good_ending_qz(part):
    return part in common_suffixes_qz
    
def is_good_prefix_qz(part):
    return is_good_part_generic(part)

# === Quechua specific  heuristics END
