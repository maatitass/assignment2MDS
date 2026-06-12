"""DCT helpers and image compression for the second MCS assignment."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image
from scipy.fft import dct, dctn, idctn


def compute_dct_matrix(size: int) -> np.ndarray:
    """Return the orthonormal DCT matrix used in the course MATLAB code."""
    if size <= 0:
        raise ValueError("La dimensione deve essere positiva")

    indexes = np.arange(size, dtype=float)
    alpha = np.full(size, np.sqrt(2.0 / size), dtype=float)
    alpha[0] = 1.0 / np.sqrt(size)

    matrix = np.empty((size, size), dtype=float)
    for k in range(size):
        matrix[k, :] = alpha[k] * np.cos(k * np.pi * (2 * indexes + 1) / (2 * size))
    return matrix


def dct_1d_fast(values: np.ndarray) -> np.ndarray:
    """Compute the fast 1D DCT with the scaling required by the PDF tests."""
    return dct(np.asarray(values, dtype=float), type=2, norm="ortho")


def dct_1d_homemade(values: np.ndarray) -> np.ndarray:
    """Compute the 1D DCT with explicit matrix multiplication."""
    values = np.asarray(values, dtype=float)
    return compute_dct_matrix(values.size) @ values


def dct_2d_homemade(block: np.ndarray) -> np.ndarray:
    """Compute a 2D DCT with explicit matrix multiplication."""
    data = _as_square_float_matrix(block)
    matrix = compute_dct_matrix(data.shape[0])
    return matrix @ data @ matrix.T


def dct_2d_fast(block: np.ndarray) -> np.ndarray:
    """Compute the fast library 2D DCT."""
    data = np.asarray(block, dtype=float)
    if data.ndim != 2:
        raise ValueError("La DCT2 richiede una matrice bidimensionale")
    return dctn(data, type=2, norm="ortho")


def idct_2d_fast(coefficients: np.ndarray) -> np.ndarray:
    """Compute the inverse fast library 2D DCT."""
    data = np.asarray(coefficients, dtype=float)
    if data.ndim != 2:
        raise ValueError("La IDCT2 richiede una matrice bidimensionale")
    return idctn(data, type=2, norm="ortho")


def frequency_keep_mask(block_size: int, cutoff: int) -> np.ndarray:
    """Keep coefficients with k + ell < cutoff, using zero-based frequencies."""
    _validate_block_parameters(block_size, cutoff)
    rows, cols = np.indices((block_size, block_size))
    return rows + cols < cutoff


def compress_image_array(
    image: np.ndarray,
    block_size: int,
    cutoff: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Compress a grayscale image array by cutting high DCT frequencies."""
    _validate_block_parameters(block_size, cutoff)
    data = np.asarray(image)
    if data.ndim != 2:
        raise ValueError("L'immagine deve essere in scala di grigi")

    height, width = data.shape
    cropped_height = (height // block_size) * block_size
    cropped_width = (width // block_size) * block_size
    if cropped_height == 0 or cropped_width == 0:
        raise ValueError("L'immagine e' piu' piccola del blocco scelto")

    original = data[:cropped_height, :cropped_width].astype(np.uint8, copy=True)
    compressed = np.zeros_like(original, dtype=float)
    mask = frequency_keep_mask(block_size, cutoff)

    for top in range(0, cropped_height, block_size):
        for left in range(0, cropped_width, block_size):
            block = original[top : top + block_size, left : left + block_size].astype(float)
            coefficients = dct_2d_fast(block)
            coefficients[~mask] = 0.0
            reconstructed = idct_2d_fast(coefficients)
            compressed[top : top + block_size, left : left + block_size] = reconstructed

    compressed_uint8 = np.clip(np.rint(compressed), 0, 255).astype(np.uint8)
    return original, compressed_uint8


def load_bmp_grayscale(path: str | Path) -> np.ndarray:
    """Load a BMP image and convert it to grayscale."""
    image_path = Path(path)
    if image_path.suffix.lower() != ".bmp":
        raise ValueError("Il file deve essere una immagine .bmp")
    with Image.open(image_path) as image:
        return np.array(image.convert("L"))


def save_grayscale_image(path: str | Path, image: np.ndarray) -> None:
    """Save a grayscale uint8 image."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.asarray(image, dtype=np.uint8)).save(output_path)


def compress_image_file(
    input_path: str | Path,
    output_path: str | Path,
    block_size: int,
    cutoff: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Load, compress, and save a BMP image."""
    image = load_bmp_grayscale(input_path)
    original, compressed = compress_image_array(image, block_size, cutoff)
    save_grayscale_image(output_path, compressed)
    return original, compressed


def time_function(function, *args, repeats: int = 3) -> float:
    """Return the best elapsed time over a few repeats."""
    best = float("inf")
    for _ in range(repeats):
        start = perf_counter()
        function(*args)
        best = min(best, perf_counter() - start)
    return best


def _as_square_float_matrix(block: np.ndarray) -> np.ndarray:
    data = np.asarray(block, dtype=float)
    if data.ndim != 2:
        raise ValueError("La DCT2 richiede una matrice bidimensionale")
    if data.shape[0] != data.shape[1]:
        raise ValueError("La DCT fatta in casa usa matrici quadrate")
    return data


def _validate_block_parameters(block_size: int, cutoff: int) -> None:
    if block_size <= 0:
        raise ValueError("F deve essere un intero positivo")
    if cutoff < 0 or cutoff > 2 * block_size - 2:
        raise ValueError("d deve rispettare 0 <= d <= 2F - 2")
