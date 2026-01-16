import os
import torch
import clip
from PIL import Image
from tqdm import tqdm

def select_keyframes_and_remove_others(frame_dir, keep_ratio=0.3):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    image_paths = sorted([os.path.join(frame_dir, f) for f in os.listdir(frame_dir) if f.endswith('.jpg')])
    image_tensors = []
    valid_paths = []

    for path in tqdm(image_paths, desc="Preprocessing frames"):
        try:
            image = preprocess(Image.open(path)).unsqueeze(0).to(device)
            image_tensors.append(image)
            valid_paths.append(path)
        except:
            continue

    with torch.no_grad():
        image_features = torch.cat([model.encode_image(img) for img in image_tensors])
        image_features /= image_features.norm(dim=-1, keepdim=True)

    mean_feature = image_features.mean(dim=0)
    similarities = image_features @ mean_feature

    sorted_indices = similarities.argsort(descending=True).tolist()
    sorted_paths = [valid_paths[i] for i in sorted_indices]

    # Determine how many to keep
    k = max(1, int(len(sorted_paths) * keep_ratio))
    selected_paths = sorted_paths[:k]

    # Remove the rest
    removed = 0
    for path in sorted_paths[k:]:
        try:
            os.remove(path)
            removed += 1
        except:
            pass

    print(f"Retained {k} keyframes. Deleted {removed} non-keyframes.")
    return selected_paths
