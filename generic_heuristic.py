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