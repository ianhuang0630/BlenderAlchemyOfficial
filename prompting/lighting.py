from PIL import Image
from utils.image import horiz_concat
from tasksolver.common import Question, TaskSpec
from tasksolver.answer_types import YesNoWhy, PythonExecutableAnswer, LeftOrRight
from tasksolver.answer_types import PythonExecutableDiffAnswer, StarredList
from tasksolver.utils import docs_for_GPT4


code_editing_task = TaskSpec(name="Blender code editing for lighting refinement",
        description="You're an experienced python programmer within the Blender environment. You must change the code to make the desired lighting setup.",
        answer_type=PythonExecutableAnswer,
        followup_func=None,
        completed_func=None
)
code_editing_task.add_background(
    Question([
        "Read the following for the docs of the parser, which will parse your response, to guide the format of your responses:" , 
        docs_for_GPT4(PythonExecutableAnswer.parser) 
    ])
)

parameter_search_task = TaskSpec(
    name="Trying different values for fields within Blender code to get the right visual output",
    description="Look at the code provided and change only 1-2 lines by replacing numerical values that would better match the target.",
    # description="Look at the code provided and change only 1-2 lines by replacing numerical values with calls of the `blenderai_uniform_sample` function. Do so for variables or fields where you think trying out different combinations would maximize the success of matching the desired visual output.",
    answer_type=PythonExecutableAnswer,
    followup_func=None,
    completed_func=None
)
parameter_search_task.add_background(
    Question([
        "Read the following for the docs of the parser, which will parse your response, to guide the format of your responses:" , 
        docs_for_GPT4(PythonExecutableAnswer.parser) 
    ])
)

pruning_task = TaskSpec(name="Evaluate which rendering has a lighting setup more visually similar to some target target lighting setup.",
        description="You're an experienced Blender 3D artist with a keen eye for lighting in Blender. You must compare two different renderings and indicate which one has a lighting setup more similar to the target lighting setup.",
        answer_type=LeftOrRight,
        followup_func=None,
        completed_func=None 
)
pruning_task.add_background(
    Question([
        "Read the following for the docs of the parser, which will parse your response, to guide the format of your responses:" , 
        docs_for_GPT4(LeftOrRight.parser) 
    ])
)


def craft_eval_question(
    target_image: Image.Image,
    left_image: Image.Image,
    right_image: Image.Image,
    left_code:str,
    right_code:str,
    target_description:str=None,
    use_vision:bool=True
):
    
    if use_vision: 
        if target_image is None:
            prompt1 = [f"Our desired target lighting setup can be described by: {target_description}.",]
            prompt2 = ["Below, I show two different renders. Which one is has a lighting setup more similar to the desired lighting setup described? The one on the left or right?",]
                
        else:
            prompt1 = [("Here is an image with the desired lighting setup:" if target_description is None else f"Here's a rendering with the desired lighting setup of {target_description}:"),
                target_image]
            prompt2 = ["Below, I show two different renders. Which one is has a lighting setup more similar to the desired lighting setup? The one on the left or right?",]
                
        question_to_critic = Question([
                *prompt1,
                *prompt2, 
                horiz_concat(left_image, right_image)
            ]
        )
    else:
        assert target_description is not None
        question_to_critic = Question([f"Our desired target lighting setup can be described by: {target_description}.",
            "Imagine I'm showing you two Blender python scripts for lighting setup, and they're side by side. Which one has the highest chance of producing the desired target lighting setup in Blender? The one on the left or right?",
            f"Code on the LEFT:\n```python\n{left_code}\n```",
            f"Code on the RIGHT:\n```python\n{right_code}\n```",
            "Make sure that your final answer indicates which one has the highest chance of producing the desired lighting setup -- left or right. Answer by putting left or right in ```'s."
        ])

    return question_to_critic


def craft_tuner_question(
    blender_init_code_str:str,
    init_image:Image.Image,
    target_image: Image.Image,
    target_description:str=None,
    edit_style:str="rewrite_code",
    use_vision:bool=True):

    if use_vision:    
        if target_description is None:
            if target_image is None:
                raise ValueError("No target provided, either textual or image!")
            else:
                part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
This produces the lighting in the rendering on the left below:
"""
        else:
            if target_image is None:
                part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
This produces the lighting in the rendering below. However, the desired lighting setup we'd like to create is the target lighting setup described by: {target_description}
"""
            else:
                part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
This produces the lighting in the rendering on the left below. The lighting in the rendering on the right is the target lighting setup: {target_description}:
"""
                
        if target_image is None:
            part2 = f"""
The desired lighting setup is described by {target_description}.
Answer the following questions:
1) What is the SINGLE most visually obvious difference between the lighting in the image above and the desired lighting described?
2) Look at the code. Which fields/variables which are set to numerical values are most likely responsible for the obvious visual difference in your answer to question 1?
3) Copy the code above (COPY ALL OF IT) and replace the assignments of such fields/variables accordingly!
"""
        else: 
            part2 = f"""
The desired lighting setup is in the image on the right. 
Answer the following questions:
1) What is the SINGLE most visually obvious difference between the two lightings in the two renderings in the image above?
2) Look at the code. Which fields/variables which are set to numerical values are most likely responsible for the obvious visual difference in your answer to question 1?
3) Copy the code above (COPY ALL OF IT) and replace the assignments of such fields/variables accordingly!
"""
    else:
        part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
However, the desired lighting setup we'd like to create is the target lighting described by {target_description}
""" 
        part2 = f"""
The desired lighting setup is described by {target_description}.
Answer the following questions:
1) What is the SINGLE most obvious difference between the lighting setup that would be generated by the code and the desired lighting described?
2) Look at the code. Which fields/variables which are set to numerical values are most likely responsible for the obvious difference in your answer to question 1?
3) Copy the code above (COPY ALL OF IT) and replace the assignments of such fields/variables accordingly!
"""

    if edit_style == "rewrite_code":
        part2 += """
MAKE SURE YOUR CODE IS RUNNABLE. MAKE SURE THAT THE ENERGY LEVELS OF THE LIGHTS ARE NOT OVEREXPOSING OBJECTS WITHIN THE SCENE! KEEP ENERGY OF EACH LIGHT LESS THAN 15.
DO NOT BE BRIEF IN YOUR CODE. DO NOT ABBREVIATE YOUR CODE WITH "..." -- TYPE OUT EVERYTHING."""


    if use_vision:
        tuner_question = Question([ 
                            part1,
                            (init_image if target_image is None else 
                                horiz_concat(left=init_image,
                                            right=target_image)),
                            part2
                            ])
    else:
        tuner_question = Question([part1, part2])
    return tuner_question



def craft_leap_question(blender_init_code_str:str,
                        init_image:Image.Image,
                        target_image:Image.Image,
                        target_description:str=None,
                        edit_style:str="rewrite_code",
                        use_vision=True):

    if use_vision: 
        if target_description is None:
            if target_image is None:
                raise ValueError("No target provided, either textual or image!")
            else:
                part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
This produces the lighting in the rendering on the left below:
"""
        else:
            if target_image is None:
                part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
This produces the lighting in the rendering below. However, the desired lighting setup we'd like to create is the target lighting setup described by: {target_description}
"""
            else:
                part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
This produces the lighting in the rendering on the left below. The lighting in the rendering on the right is the target lighting setup: {target_description}:
"""

        if target_image is None: 
            part2 = f"""
The desired lighting setup is previously described. Imagine that desired target lighting setup. Please describe the difference between the lighting shown and the desired target lighting setup, and edit the code above to reflect this desired change. Pay special attention to the color of the lights.
MAKE SURE YOUR CODE IS RUNNABLE. MAKE SURE THAT THE ENERGY LEVELS OF THE LIGHTS ARE NOT OVEREXPOSING OBJECTS WITHIN THE SCENE! KEEP ENERGY OF EACH LIGHT LESS THAN 15.
DO NOT BE BRIEF IN YOUR CODE. DO NOT ABBREVIATE YOUR CODE WITH "..." -- TYPE OUT EVERYTHING.
"""

        else:
            part2 = f"""
The desired lighting setup is shown in the image on the right. Please describe the difference between the two lighting setups, and edit the code above to reflect this desired change. Pay special attention to the base color of the lights.
MAKE SURE YOUR CODE IS RUNNABLE. MAKE SURE THAT THE ENERGY LEVELS OF THE LIGHTS ARE NOT OVEREXPOSING OBJECTS WITHIN THE SCENE! KEEP ENERGY OF EACH LIGHT LESS THAN 15.
DO NOT BE BRIEF IN YOUR CODE. DO NOT ABBREVIATE YOUR CODE WITH "..." -- TYPE OUT EVERYTHING.
"""
    else:
       
        part1 = f"""
The following Blender code was used to produce a lighting setup:
```python
{blender_init_code_str}
```
However, the desired lighting setup we'd like to create is the target lighting described by {target_description}
""" 
        part2 = f"""
The desired lighting setup is previously described. Imagine that desired target lighting setup. Please describe the difference between the lighting shown and the desired target lighting setup, and edit the code above to reflect this desired change. Pay special attention to the color of the lights.
MAKE SURE YOUR CODE IS RUNNABLE. MAKE SURE THAT THE ENERGY LEVELS OF THE LIGHTS ARE NOT OVEREXPOSING OBJECTS WITHIN THE SCENE! KEEP ENERGY OF EACH LIGHT LESS THAN 15.
DO NOT BE BRIEF IN YOUR CODE. DO NOT ABBREVIATE YOUR CODE WITH "..." -- TYPE OUT EVERYTHING.
"""

        
    if use_vision:
        leap_question = Question([ 
                                part1,
                                (init_image if target_image is None else 
                                    horiz_concat(left=init_image,
                                                right=target_image)),
                                part2
                                ])

    else:
        leap_question = Question([part1, part2])
    return leap_question 