
# ExactSuperpixels


## Key Features

- **Exact Superpixel Count**: Unlike standard SLIC implementations, ExactSuperpixels guarantees **the exact number of superpixels requested**.
- **Adaptive Segmentation**: Automatically adjusts the initial oversegmentation and merges regions to achieve the desired superpixel count.
- **Robust Merging Strategy**: Employs a sophisticated method to merge smaller segments while maintaining image structure.
- **Flexible Parameter Control**: Allows fine-tuning of compactness and smoothing parameters for optimal results.
  
## Example
![Object with background](./display/obj.png)

## Installation

To use ExactSuperpixels, you'll need Python 3.6+ and the following dependencies:

```bash
pip install numpy scikit-image matplotlib
```

## Usage

Here's a simple example of how to use the `exact_num_superpixels` function:

```python
import numpy as np
from skimage import io
from exactsuperpixels import exact_num_superpixels

# Load an image
image = io.imread('path_to_your_image.jpg')

# Generate superpixels
n_desired = 100  # Desired number of superpixels
segments = exact_num_superpixels(image, n_desired, compactness=10, sigma=0)

# Now 'segments' contains the superpixel labels
```

## Function Description

```python
def exact_num_superpixels(image, n_desired, compactness=10, sigma=0):
    """
    Get the exact number of superpixels in an image.
    
    Args:
        image (ndarray): Input image of shape [H, W, 3].
        n_desired (int): The desired number of superpixels.
        compactness (float): Parameter used in SLIC. Higher values make superpixels more compact.
        sigma (float): Width of Gaussian smoothing kernel for pre-processing.

    Returns:
        ndarray: Integer mask of shape [H, W] indicating superpixel labels.
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

    if len(np.unique(segments)) != n_desired:
        raise ValueError("debug needed")
    return segments
```

## How It Works

1. **Initial Oversegmentation**: The function starts by creating more superpixels than desired using the SLIC algorithm.

2. **Adjustment Process**:
   - If there are too few superpixels, it increases the number and tries again.
   - If there are too many, it begins a merging process.

3. **Merging Process**:
   - Identifies the smallest superpixel.
   - Finds its neighboring superpixels.
   - Merges the smallest superpixel with its smallest neighbor.
   - Repeats until the desired number of superpixels is reached.

4. **Validation**: Ensures the final number of superpixels matches the desired count.

## Contributing

Contributions to this project are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This implementation is based on the SLIC algorithm from scikit-image.
- Special thanks to the scikit-image and NumPy communities for their excellent libraries.
