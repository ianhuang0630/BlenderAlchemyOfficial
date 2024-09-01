from typing import Type, List, Union
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
import io

def plot_image_grid(images:List[Image.Image], rows:int, cols:int,
                    titles:Union[None, List[str]]=None) -> matplotlib.figure.Figure:
    """
    Arrange a list of images into a grid and plot them using matplotlib.

    Args:
    images (list): A list of PIL images.
    rows (int): Number of rows in the grid.
    cols (int): Number of columns in the grid.
    """

    # TODO: handle the case when the num rows is 1
    fig, axes = plt.subplots(rows, cols, figsize=(cols*3, rows*3))
    for i in range(rows):
        for j in range(cols):
            idx = i * cols + j

            if rows > 1 and cols > 1:
                my_axes = axes[i,j]
            elif rows == 1 and cols > 1:
                my_axes = axes[j] 
            elif rows == 1 and cols == 1: 
                my_axes = axes
                
            if idx < len(images) and isinstance(images[idx], Image.Image):
                my_axes.imshow(images[idx])
                my_axes.axis("off")
                if titles is not None:
                    my_axes.set_title(titles[idx])
            else:
                if rows > 1:
                    my_axes.axis("off")
                else:   
                    my_axes.axis("off")
    plt.tight_layout()
    return fig


def pltfig_to_PIL(fig: matplotlib.figure.Figure) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    return image


def horiz_concat(left:Image.Image, right:Image.Image) -> Image.Image:
    """
    Concatenate two PIL.Image objects horizontally.

    Parameters:
    - left: PIL.Image - The first image to be concatenated.
    - right: PIL.Image - The second image to be concatenated.

    Returns:
    - PIL.Image - The horizontally concatenated image.
    """

    if left.size != right.size: 
        right = right.resize(left.size)

    assert right.size == left.size
    
    # Ensure that both images have the same height
    # Get the heights of the two images
    height1 = left.height
    height2 = right.height
    # Find the minimum height of the two images
    min_height = min(height1, height2)
    # Resize both images to have the same height
    left_resized = left.resize((int(left.width * (min_height / height1)), min_height))
    right_resized = right.resize((int(right.width * (min_height / height2)), min_height))
    # Calculate the width of the concatenated image
    new_width = left_resized.width + right_resized.width
    # Create a new image with the calculated width and the height of either image
    concatenated_image = Image.new('RGB', (new_width, min_height))
    # Paste the resized first image onto the new image
    concatenated_image.paste(left_resized, (0, 0))
    # Paste the resized second image next to the first one
    concatenated_image.paste(right_resized, (left_resized.width, 0))

    return concatenated_image

