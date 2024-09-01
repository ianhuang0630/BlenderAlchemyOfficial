import sys
import numpy as np
from PIL import Image

import torch
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from transformers import CLIPProcessor, CLIPModel



def clip_similarity(image1, image2):
    """
    Compute the CLIP similarity between two PIL images.

    Args:
    image1 (PIL.Image): The first input image.
    image2 (PIL.Image): The second input image.

    Returns:
    float: The CLIP similarity between the two images.
    """
    if image1.size != image2.size:
        image2 = image2.resize(image1.size)

    # Load the CLIP model
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    # Load the CLIP processor
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Preprocess the images
    images = [image1, image2]
    inputs = processor(images=images, return_tensors="pt")

    # Compute the features for the images
    with torch.no_grad():
        features = model.get_image_features(**inputs)

    # Compute the cosine similarity between the image features
    sim = torch.nn.functional.cosine_similarity(features[0], features[1], dim=-1)

    return sim.item()

def photometric_loss(image1:Image.Image, image2:Image.Image) -> float:
    """
    Compute the photometric loss between two PIL images.

    Args:
    image1 (PIL.Image): The first input image.
    image2 (PIL.Image): The second input image.

    Returns:
    float: The photometric loss between the two images.
    """

    if image1.size != image2.size:
        image2 = image2.resize(image1.size)
    
    # Convert images to numpy arrays
    img1_array = np.array(image1)[:, :, :3]
    img2_array = np.array(image2)[:, :, :3]

    # Normalize images to [0, 1]
    img1_norm = img1_array.astype(np.float32) / 255.0
    img2_norm = img2_array.astype(np.float32) / 255.0

    # Compute the squared difference between the normalized images
    diff = np.square(img1_norm - img2_norm)

    # Compute the mean squared error
    mse = np.mean(diff)
    return mse

    
def img2text_clip_similarity(image, text):
    """
    Compute the CLIP similarity between a PIL image and a text.

    Args:
    image (PIL.Image): The input image.
    text (str): The input text.

    Returns:
    float: The CLIP similarity between the image and the text.
    """
    
    # Load the CLIP model
    # model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

    # Load the CLIP processor
    # processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

    # Preprocess the image and text
    inputs = processor(text=text, images=image, return_tensors="pt")

    # Compute the features for the image and text
    with torch.no_grad():
        image_features = model.get_image_features(pixel_values=inputs.pixel_values)
        text_features = model.get_text_features(input_ids=inputs.input_ids)

    # Compute the cosine similarity between the image and text features
    sim = torch.nn.functional.cosine_similarity(image_features, text_features, dim=-1)

    return sim.item()

    
def img2img_clip_similarity(image1, image2):
    """
    Compute the CLIP similarity between two PIL images.

    Args:
    image1 (PIL.Image): The first input image.
    image2 (PIL.Image): The second input image.

    Returns:
    float: The CLIP similarity between the two images.
    """
    
    if image1.size != image2.size:
        image2 = image2.resize(image1.size)

    # Load the CLIP model
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    # Load the CLIP processor
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Preprocess the images
    images = [image1, image2]
    inputs = processor(images=images, return_tensors="pt")

    # Compute the features for the images
    with torch.no_grad():
        features = model.get_image_features(**inputs)

    # Compute the cosine similarity between the image features
    sim = torch.nn.functional.cosine_similarity(features[0], features[1], dim=-1)

    return sim.item()


if __name__ == "__main__":
    photo_loss_before = photometric_loss(
                                    Image.open("init_render.png"),
                                    Image.open("target_render.png"))

    photo_loss_after = photometric_loss(
        Image.open("material_render_outputs/65cbc5df19880de1d1d762db.png"),
        Image.open("target_render.png"))

    similarity_score_before = clip_similarity(
        Image.open("init_render.png"),
        Image.open("target_render.png"))

    similarity_score_after = clip_similarity(
        Image.open("material_render_outputs/65cbc5df19880de1d1d762db.png"),
        Image.open("target_render.png"))

    print("photometric: ", photo_loss_before, "-->", photo_loss_after)
    print("Similarity: ", similarity_score_before, "-->", similarity_score_after)


