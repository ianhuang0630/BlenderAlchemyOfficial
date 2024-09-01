import os
import numpy as np
import subprocess
import re
import copy
from tasksolver.exceptions import CodeExecutionException, ToolCallException
from pathlib import Path

def edit_code(code_str:str, code_before:str, code_after:str):
    """
    Args:
        code_str: a string containing multiple lines of python code.
        code_before: a string containing lines that should be replaced by code in `code_after`
        code_after: a string containing lines that replace the code in `code_before`
    Returns:
        modified_code_str: a string containing the modified code.
    Raises:
        ToolCallException when the code replacement/editing cannot be done.
    """ 
    code_before = code_before.strip()
    code_after = code_after.strip()

    start_idx = code_str.find(code_before)
    if start_idx == -1:
        raise ToolCallException("Code to replace not found")
    
    # Replace `code_before` with `code_after` in `code_str`
    end_idx = start_idx + len(code_before)
    modified_code_str = code_str[:start_idx] + code_after + code_str[end_idx:]
    return modified_code_str


def add_line_numbers(code_string:str, delimiter:str="|"):
    """
    Args:
        code_string: code string
        delimiter: the symbol that separates the line number and the line of code.
                e.g. "|" leads to '10| print("hello world")'
    """
    numbered_code_string = "\n".join([str(line_number+1)+delimiter+" "+el for line_number, el in enumerate(code_string.split("\n"))])
    return numbered_code_string


def get_code_as_string(script_path):
    with open(script_path, 'r') as f:
        code_str = f.read()
    return code_str


def blenderai_uniform_sample(low:float, high:float, num_samples:int):
    """
    Args:
        low: lower bound of the range being sampled from
        high: higher bound of the range being sampled from 
        num_samples: Number of samples in that range. Should be positive.
    """
    assert low <= high
    assert num_samples > 0
    return np.linspace(low, high, num_samples) 


def get_macroed_code(code_str):
    uniform_sample_regex = r'blenderai_uniform_sample\s*\([^)]*\)'
    instances = re.findall(uniform_sample_regex, code_str)
    # each of these instances should be a possible version
    # of the script.
    if len(instances) == 0:
        return [code_str]
    
    ranges = []
    for ins in instances:
        try:
            options = eval(ins) 
        except:
            raise CodeExecutionException
        ranges.append(options)

    parameter_space = np.stack ([el.flatten() for el in np.meshgrid(*ranges)])
    parameter_space = parameter_space.transpose()    
    
    def replace_matches_with_list(input_string, pattern, replacements):
        def replace(match):
            return replacements.pop(0)
        return re.sub(pattern, replace, input_string)

    code_instances = [] 
    for param_instance in parameter_space:
        string_params = [str(el) for el in param_instance] 
        code_instance = replace_matches_with_list(code_str, uniform_sample_regex, string_params)
        code_instances.append(code_instance)

    return code_instances
    

def get_macroed_code_as_string(script_path):
    with open(script_path , 'r') as f: 
        code_str = f.read()
    return get_macroed_code(code_str)
   

def get_code_diffs(before:Path, after: Path):
    """
    Args:
        before: path to before
        after: path to after
    Returns:
        list of tuples, (change_type, additional_info_dictionary)
    """
    assert os.path.exists(str(before)) and os.path.exists(str(after))
    
    completed_process = subprocess.run(["diff", str(before), str(after)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_str = completed_process.stdout.decode("utf-8")
    
    changes = []
    
    mode = None
    data = {}
    
    for line in output_str.split("\n"):
        if len(line.strip()) > 0:
            # if  the line doesn't start with > or <, or ---, then it's a LABEL.
            if not (line.startswith(">") or line.startswith("<") or line.startswith("---")):
                if mode is not None: 
                    changes.append((mode, data))
                # a -- what's being added?
                if "a" in line:
                    mode = "add"
                    data = {"added_lines":[]}
                # c -- what's being changed?
                elif  "c" in line:
                    mode = "change"
                    data = {"deleted_lines": [], "added_lines": []}
                # d -- how much is being deleted?
                elif "d" in line:
                    mode = "delete"
                    data = {"deleted_lines": []}
                else:
                    raise ValueError(f"Couldn't determine the mode of {line}")
            else:
                assert mode is not None, f"mode not set. Something wrong with the output:\n{output_str}"
        
                if mode == "change":
                    if line.startswith("<"): # this is what's being removed
                        deleted = line[1:].strip()
                        data["deleted_lines"].append(deleted)
                        
                    elif line.startswith(">"): # this siw hat's being added
                        added = line[1:].strip()
                        data["added_lines"].append(added)
                    elif line.startswith("---"):
                        pass
                    else:
                        raise ValueError(f"unexpected line in mode {mode}: {line}")
        
                if mode == "delete":
                    if line.startswith("<"): # this is waht's being removed
                        deleted = line[1:].strip()
                        data ["deleted_lines"].append(deleted)
                    else:
                        raise ValueError(f"unexpected line in mode {mode}: {line}")
                        
                if mode == "add":
                    if line.startswith(">"):
                        added = line[1:].strip()
                        data["added_lines"].append(added)
                    else:
                        raise ValueError(f"unexpected line in mode {mode}: {line}")
    
    # sync  mode + data
    if mode is not None:
        changes.append((mode, data))

    return changes
    
def tally_total_changes(changes_list):
    num_adds = 0
    num_dels = 0
    num_changes = 0

    num_added_lines = 0
    num_added_chars = 0
    num_deleted_lines = 0
    num_deleted_chars = 0

    for cl in changes_list:
        if cl[0] == 'add': 
            num_adds += 1
        elif cl[0] == "delete":
            num_dels += 1
        elif cl[0] == "change":
            num_changes += 1

        if cl[0] in ("add", "change"):
            num_added_lines += len(cl[1]["added_lines"])
            num_added_chars += sum([len(el.strip()) for el in cl[1]["added_lines"]])
    
        if cl[0] in ("delete", "change"):
            num_deleted_lines += len(cl[1]["deleted_lines"])
            num_deleted_chars += sum([len(el.strip()) for el in cl[1]["deleted_lines"]])
            
    return {"num_adds": num_adds, "num_dels": num_dels, "num_changes": num_changes,
            "num_added_lines": num_added_lines, "num_added_chars": num_added_chars,
            "num_deleted_lines": num_deleted_lines, "num_deleted_chars": num_deleted_chars
           }




if __name__ == "__main__":

    code = """
a = blenderai_uniform_sample (9, 12, 2)
b = blenderai_uniform_sample (-1, 2, 3)
c = a + b
"""
    # # Regex pattern to find calls to uniform_sample()
    # pattern = r'uniform_sample\s*\([^)]*\)'

    # # Find all matches
    # matches = re.findall(pattern, code)
 
    out = get_macroed_code(code)
    import ipdb; ipdb.set_trace()

    # form the universe of possible script instances.
            
    

    # # Example usage
    # code = """
    # uniform_sample()
    # some_var = uniform_sample(1, 10)
    # result = uniform_sample(0, 1, size=10)
    # """

    # pattern = r'uniform_sample\s*\([^)]*\)'
    # replacements = ["new_func1()", "new_func2()", "new_func3()"]

    # new_code = replace_matches_with_list(code, pattern, replacements)
    # print(new_code)




    



    


    



