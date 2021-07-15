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