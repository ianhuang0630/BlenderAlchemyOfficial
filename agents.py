
import sys
import os
import subprocess
import matplotlib.pyplot as plt
from pathlib import Path
import json
from bson import ObjectId
from PIL import Image
import random

from utils.image import horiz_concat, plot_image_grid, pltfig_to_PIL
from utils.code import get_code_as_string, get_macroed_code

from loguru import logger
import threading
import time
import io
from utils.code import get_code_as_string, edit_code

# agent and task setup
from tasksolver.agent import Agent
from tasksolver.event import *
from tasksolver.common import ParsedAnswer, TaskSpec, Question 
from tasksolver.exceptions import GPTOutputParseException, CodeExecutionException, ToolCallException
from tasksolver.utils import docs_for_GPT4
from tasksolver.answer_types import YesNoWhy, PythonExecutableAnswer, LeftOrRight
from tasksolver.answer_types import PythonExecutableDiffAnswer, StarredList
from tasksolver.keychain import KeyChain
from tqdm import tqdm


class GeneralAgent(Agent): 
    """
    Agent that answers questions in a certain format.
    """
    def __init__(self, api_key:str, task:TaskSpec,
                 vision_model:str="gpt-4-turbo" 
                 ):
        super().__init__(api_key=api_key,  task=task,
                        vision_model=vision_model,
                        followup_func=self.followup_func)
                        
    def think(self, question: Question, num_tokens: int, agent_idx: int) -> ParsedAnswer:
        p_ans, ans, meta, p = self.visual_interface.run_once(question, max_tokens=num_tokens)
        return p_ans

    def act(self, p_ans:ParsedAnswer, script_save:Path, render_save:Path, iteration:int,
            blender_file:str, blender_script:str, config:dict, blender_step):

        # Executes the code based on the results from think
        script_id = str(ObjectId())
        code_path = str(script_save / (f"{iteration}_" + script_id + ".py"))
        render_path = str(render_save / (f"{iteration}_" + script_id + ".png"))

        with open(code_path, "w")  as f:
            f.write(p_ans.code)
        
        # now run the blender program
        blender_step(config, blender_file, blender_script, code_path, render_path)
        return code_path, render_path

    @staticmethod
    def followup_func(agent):
        feedback_question = None
        return feedback_question


class EditCodeAgent(object): 
    """
    Instead of rewriting code from scratch, this agent edits code by specifying before and after code blocks.
    """
    def __init__(self, api_key:str, task:TaskSpec,
                 vision_model:str="gpt-4-vision-preview",):
        
        # we break  this tasks into two substeps:
        # 1) brainstorming the changes that we require to the code
        self.brainstorming_task = TaskSpec(
            name="List of changes to make to the code",
            description="",
            answer_type=StarredList,
            followup_func=None,
            completed_func=None
        ) 
        self.brainstorming_model = Agent(
                                    api_key, 
                                    task=self.brainstorming_task, 
                                    vision_model=vision_model).visual_interface

        # ...and 2) actually predicting the line-by-line changes that are needed.
        self.code_delta_task = TaskSpec(
            name="Translating a desired change into actual code changes",
            description="",
            answer_type=PythonExecutableDiffAnswer,
            followup_func=None,
            completed_func=None
        )
        self.code_delta_model = Agent(
                                    api_key,
                                    task=self.code_delta_task,
                                    vision_model=vision_model).visual_interface
                                
    def think(self, question:Question,
                num_tokens: int, agent_idx=None) -> ParsedAnswer:


        if agent_idx is None:
            prepend_string = ""
        else: 
            prepend_string = f"Agent{agent_idx}: "
        
        # step 1: ask the brainstormer to create a plan
        appended_question="""
Describe, in a bullet-point list (using * as the bullet points), which lines you would change (quote them in python code blocks) and how you would change them. Every item of the list should reference a line of code and how it should be changed.
"""
        question = question + Question([appended_question])

        done = False
        tries = 0 
        max_tries = 10

        while not done and tries < max_tries: 
            logger.info(f"PLANNING ATTEMPT #{tries}")
            list_of_diffs, _, _, _ = self.brainstorming_model.rough_guess(question)
            tries += 1
            if len(list_of_diffs.list_items) == 0:
                logger.warning(prepend_string + f"retrying ({tries})...")
                continue # reform plan.
                
            logger.info(prepend_string + "Goals:"+"\n\n".join(list_of_diffs.list_items)) 

            # step 2: Translate into concrete edits proposals.
            code2llm = PythonExecutableAnswer.parser(str(question)).code
            diffs_to_implement = [] 
            replan = False
            
            for goal in list_of_diffs.list_items:
                prompt = f"""
You'd like to do the following: {goal}
Convert this into a concrete code difference indicated by "Before:" and "After:" labels,
followed by python code blocks that indicate which line should be
changed, and to what.

Example:

Before:
```python
a = 1
```
After:
```python
a = 2 
```
"""
                delta_question = Question(
                [
                    f'Consider the following code in Blender:\n```python\n{code2llm}```',
                    prompt
                ] 
                )

                delta_done = False
                delta_tries = 0
                delta_max_tries = 10
                while not delta_done and delta_tries < delta_max_tries:
                    try:
                        diff, _, _, _ = self.code_delta_model.rough_guess(delta_question)
                        tries += 1
                        delta_done = True
                    except GPTOutputParseException as e:
                        logger.warning(prepend_string + f"Parsing of code delta for goal {goal} failed: {str(e)}")
                        logger.warning(prepend_string + f"retrying delta extraction ({delta_tries})...")

            
                # try to find the code snippet, if it isn't there, something is likely wrong with the plan.
                try: 
                    edit_code(code2llm, diff.code_from, diff.code_to)
                    diffs_to_implement.append(diff)
                except ToolCallException as e:
                    logger.warning(prepend_string + f"Code diff before...\n{diff.code_from}\n...not found in original code!") 
                    # logger.warning(f"REPLANNING. Execution of goal {goal} led to the following error: {str(e)}")
                    # replan = True
                    # break # breaking out of for loop to retrigger planning

            replan = len(diffs_to_implement) ==  0
            if replan: # retrigger planning
                continue # replanning
            done = True # no need to plan again.

            
        assert done, "PLANNING FAILED!" 

        edit_stages = []
        edited_code = code2llm
        # step 3: modify the code 
         
        completed_diffs = 0
        for diff in diffs_to_implement:
            try: 
                mod_code = edit_code(edited_code, diff.code_from, diff.code_to)
                completed_diffs += 1
            except ToolCallException as e:
                logger.warning(prepend_string + f"Skipping this diff, since execution of goal {goal} led to the following error: {str(e)}")
                continue
            edit_stages.append(mod_code) 
            edited_code = mod_code
            logger.info(prepend_string + "Editing done.")

        logger.info(prepend_string + f"completed/parsed/planned = {completed_diffs}/{len(diffs_to_implement)}/{len(list_of_diffs.list_items)}") 
        
        p_ans = PythonExecutableAnswer(code=edited_code)
        return p_ans

    def act(self, p_ans:ParsedAnswer, script_save:Path, render_save:Path, iteration:int, 
            blender_file:str, blender_script:str, config:dict, blender_step):

        script_id = str(ObjectId())
        code_path = str(script_save / (f"{iteration}_" + script_id + ".py"))
        render_path = str(render_save / (f"{iteration}_" + script_id + ".png"))

        with open(code_path, "w")  as f:
            f.write(p_ans.code)
        
        # now run the blender program
        blender_step(config, blender_file, blender_script, code_path, render_path)
        return code_path, render_path

    @staticmethod
    def followup_func(agent):
        feedback_question = None
        return feedback_question

