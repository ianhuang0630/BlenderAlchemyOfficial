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
            prompt1 = [f"Our desired target 3D model can be described by: {target_description}.",]
            prompt2 = ["Below, I show two different 3D models. Which one is visually more similar to the desired model described? The one on the left or right?",]
                
        else:
            prompt1 = [("Here is the target 3D model rendering:" if target_description is None else f"Here's the target 3D rendering of {target_description}:"),
                target_image]
            prompt2 = ["Below, I show two different 3D models. Which one is visually more similar to the target model rendering? The one on the left or right?",]
                
        question_to_critic = Question([
                *prompt1,
                *prompt2, 
                horiz_concat(left_image, right_image)
            ]
        )
    else:
        assert target_description is not None
        question_to_critic = Question([f"Our desired target model can be described by: {target_description}.",
            "Imagine I'm showing you two Blender python scripts that sets the shape keys of a 3D mesh, and they're side by side. Which one has the highest chance of producing the desired target model in Blender? The one on the left or right?",
            f"Code on the LEFT:\n```python\n{left_code}\n```",
            f"Code on the RIGHT:\n```python\n{right_code}\n```",
            "Make sure that your final answer indicates which one has the highest chance of producing the desired model -- left or right. Answer by putting left or right in ```'s."
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
    # The case with visual input

        if target_description is None:
            # If there is no target description

            if target_image is None:
                # No target image
                raise ValueError("No target provided, either textual or image!")
            else:
                # Target image only, not target text
                part1 = f"""
                The following Blender code was used to set the shape keys of a 3D model:
                ```python
                {blender_init_code_str}
                ```
                This produces the rendering of a 3D model on the left below:
                """
        else:
            if target_image is None:
                # No target image, but with target decription


                part1 = f"""
                The following Blender code was used to set the shape keys of a 3D model:
                ```python
                {blender_init_code_str}
                ```
                This produces the rendering of a 3D mdoel below. However, the desired model we'd like to create is the target model {target_description}
                """
            else:
                part1 = f"""
                The following Blender code was used to set the shape keys of a 3D model:
                ```python
                {blender_init_code_str}
                ```
                This produces the rendering of a 3D model on the left below. The model on the right is the target, {target_description}:
                """
                
        if target_image is None:
            # No target image, so use target_description
            part2 = f"""
            The desired model is described by {target_description}.
            Answer the following questions:
            1) What is the SINGLE most visually obvious difference between the 3D model in the image above and the desired model described?
            2) Look at the code. Which fields/variables which are set to numerical values are most likely responsible for the obvious visual difference in your answer to question 1?
            3) Copy the code above (COPY ALL OF IT) and replace the assignments of such fields/variables accordingly!
            """
        else: 
            # With target image
            part2 = f"""
            The desired shapekey is shown in the image on the right. 
            Answer the following questions:
            1) What is the SINGLE most visually obvious difference between the two models in the image above?
            2) Look at the code. Which fields/variables which are set to numerical values are most likely responsible for the obvious visual difference in your answer to question 1?
            3) Copy the code above (COPY ALL OF IT) and replace the assignments of such fields/variables accordingly!
            """
    else:
        # The case of no visual reference
        part1 = f"""
        The following Blender code was used to set the shape keys of a 3D model:
        ```python
        {blender_init_code_str}
        ```
        However, the desired model we'd like to create is the target model {target_description}
        """ 
        part2 = f"""
        The desired model is described by {target_description}.
        Answer the following questions:
        1) What is the SINGLE most obvious difference between the model that would be generated by the code and the desired model described?
        2) Look at the code. Which fields/variables which are set to numerical values are most likely responsible for the obvious difference in your answer to question 1?
        3) Copy the code above (COPY ALL OF IT) and replace the assignments of such fields/variables accordingly!
        """

    if edit_style == "rewrite_code":
        part2 += '\nDO NOT BE BRIEF IN YOUR CODE. DO NOT ABBREVIATE YOUR CODE WITH "..." -- TYPE OUT EVERYTHING.'
       
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
                        use_vision:bool=True):

    if use_vision: 
        if target_description is None:
            if target_image is None:
                raise ValueError("No target provided, either textual or image!")
            else:
                part1 = f"""
                The following Blender code was used to set the shape keys of a 3D model:
                ```python
                {blender_init_code_str}
                ```
                This produces the 3D model in the rendering on the left below:
                """                
        else:
            if target_image is None:
                part1 = f"""
                The following Blender code was used to set the shape keys of a 3D model:
                ```python
                {blender_init_code_str}
                ```
                This produces the 3D model in the rendering below. However, the desired model we'd like to create is the target model {target_description}
                """
            else:
                part1 = f"""
                The following Blender code was used to set the shape keys of a 3D model:
                ```python
                {blender_init_code_str}
                ```
                This produces the 3D model in the rendering on the left below. The model on the right is the target model {target_description}:
                """

        if target_image is None: 
            part2 = f"""
            The desired 3D model is previously described. Imagine that desired target 3D model. Please describe the difference between the model shown and the desired target model, and edit the code above to reflect this desired change. 
            """

        else:
            part2 = f"""
            The desired 3D model is shown in the image on the right. Please describe the difference between the two models, and edit the code above to reflect this desired change.
            """
    else:
        part1 = f"""
        The following Blender code was used to set the shape keys of a 3D model:
        ```python
        {blender_init_code_str}
        ```
        However, the desired model we'd like to create is the target model {target_description}
        """
        part2 = f"""
        The desired 3D model is shown in the image on the right. Please describe the difference between the two models, and edit the code above to reflect this desired change.
        """

    if edit_style == "rewrite_code":
        part2 += '\nDO NOT BE BRIEF IN YOUR CODE. DO NOT ABBREVIATE YOUR CODE WITH "..." -- TYPE OUT EVERYTHING.'

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