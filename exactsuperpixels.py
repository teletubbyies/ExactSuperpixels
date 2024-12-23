from skimage.segmentation import slic
from skimage.measure import regionprops
from scipy.ndimage import binary_dilation, generate_binary_structure
import numpy as np

def exact_num_superpixels(image, n_desired, compactness=10, sigma=0):
    """
        Get the exact number of superpixels in an image.
    Args:
        image: [H, W, 3].
        n_desired: int. The expected number of superpixels.
        compactness: parameter used in slic.
        sigma: parameter used in slic.

    Returns:
        segments:[H, W]. Integer mask indicating segment labels and each pixel has its own superpixel(label).
    """
    # Start with more superpixels than desired
    n_segments = int(n_desired * 1.15)

    while True:
        # Perform SLIC
        segments = slic(image, n_segments=n_segments, compactness=compactness, sigma=sigma)

        # Count unique labels
        unique_labels = np.unique(segments)
        n_current = len(unique_labels)

        if n_current >= n_desired:
            break

        # If we have too few, increase n_segments and try again
        n_segments = int(n_segments * 1.1)

    # If we have exactly the right number, we're done
    if n_current == n_desired:
        return segments

    # Always have too many at this step, merge the smallest regions
    while n_current > n_desired:
        # Find the smallest region
        props = regionprops(segments)
        smallest_region = min(props, key=lambda x: x.area)
        smallest_label = smallest_region.label

        # Create a mask for the smallest region
        mask = segments == smallest_label

        # Dilate the mask to find neighbors
        struct = generate_binary_structure(2, 2)
        dilated = binary_dilation(mask, structure=struct)

        # Find unique labels in the dilated region, excluding the smallest label itself
        neighbor_labels = np.unique(segments[dilated & ~mask])

        if len(neighbor_labels) > 0:
            # Merge with the smallest neighbor
            merge_label = min(neighbor_labels, key=lambda x: np.sum(segments == x))
            segments[segments == smallest_label] = merge_label
            n_current -= 1 # Subtract the smallest region.
        else:
            raise ValueError("The smallest region has no neighbors.")

    return segments
