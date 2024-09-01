import json

def get_candidate_and_winner(topdir, type:str="image"):
    thought_process_jsons = sorted((topdir/"thought_process").iterdir())
    data = []
    for thought_process_json in thought_process_jsons:  
        with open(thought_process_json, 'r') as f:
            foo = json.load(f)
            data.append(foo)
    
    winner_per_depth = []
    candidates_per_depth = []
    
    for data_per_depth in data:
        winner_this_depth = None
        candidates_this_depth = []
        for loginfo in data_per_depth: # depth 1
            if loginfo["phase"].startswith("explode_options_"):
                candidates_this_depth.extend(loginfo[f"choices_{type}"])  # code @ ["choices_code"]
            if loginfo["phase"].startswith("selection"):
                winner_this_depth = loginfo[f"winner_{type}"]  # code @ ["winner_code"]
        winner_per_depth.append(winner_this_depth)
        candidates_per_depth.append(candidates_this_depth)
    return candidates_per_depth , winner_per_depth