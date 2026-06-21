"""Small tests for the second MCS assignment."""

from __future__ import annotations

import numpy as np

from dct_utils import (
    compress_image_array,
    dct_1d_fast,
    dct_1d_homemade,
    dct_2d_fast,
    dct_2d_homemade,
    frequency_keep_mask,
    idct_2d_fast,
)
from gui import build_compression_preview, describe_parameter_hints, fit_preview_size, load_original_preview
from run_assignment import DEFAULT_SIZES


PDF_BLOCK = np.array(
    [
        [231, 32, 233, 161, 24, 71, 140, 245],
        [247, 40, 248, 245, 124, 204, 36, 107],
        [234, 202, 245, 167, 9, 217, 239, 173],
        [193, 190, 100, 167, 43, 180, 8, 70],
        [11, 24, 210, 177, 81, 243, 8, 112],
        [97, 195, 203, 47, 125, 114, 165, 181],
        [193, 70, 174, 167, 41, 30, 127, 245],
        [87, 149, 57, 192, 65, 129, 178, 228],
    ],
    dtype=float,
)


def test_dct_1d_matches_pdf_row_example() -> None:
    expected = np.array([4.01e2, 6.60e0, 1.09e2, -1.12e2, 6.54e1, 1.21e2, 1.16e2, 2.88e1])
    actual = dct_1d_fast(PDF_BLOCK[0])
    assert np.allclose(actual, expected, rtol=8e-3, atol=0.8)


def test_homemade_dct_1d_matches_pdf_row_example() -> None:
    expected = np.array([4.01e2, 6.60e0, 1.09e2, -1.12e2, 6.54e1, 1.21e2, 1.16e2, 2.88e1])
    actual = dct_1d_homemade(PDF_BLOCK[0])
    assert np.allclose(actual, expected, rtol=8e-3, atol=0.8)


def test_dct_2d_matches_pdf_block_example() -> None:
    expected = np.array(
        [
            [1.11e3, 4.40e1, 7.59e1, -1.38e2, 3.50e0, 1.22e2, 1.95e2, -1.01e2],
            [7.71e1, 1.14e2, -2.18e1, 4.13e1, 8.77e0, 9.90e1, 1.38e2, 1.09e1],
            [4.48e1, -6.27e1, 1.11e2, -7.63e1, 1.24e2, 9.55e1, -3.98e1, 5.85e1],
            [-6.99e1, -4.02e1, -2.34e1, -7.67e1, 2.66e1, -3.68e1, 6.61e1, 1.25e2],
            [-1.09e2, -4.33e1, -5.55e1, 8.17e0, 3.02e1, -2.86e1, 2.44e0, -9.41e1],
            [-5.38e0, 5.66e1, 1.73e2, -3.54e1, 3.23e1, 3.34e1, -5.81e1, 1.90e1],
            [7.88e1, -6.45e1, 1.18e2, -1.50e1, -1.37e2, -3.06e1, -1.05e2, 3.98e1],
            [1.97e1, -7.81e1, 9.72e-1, -7.23e1, -2.15e1, 8.13e1, 6.37e1, 5.90e0],
        ]
    )
    actual = dct_2d_fast(PDF_BLOCK)
    assert np.allclose(actual, expected, rtol=2e-2, atol=1.5)


def test_homemade_dct_2d_matches_fast_dct_2d() -> None:
    image = np.arange(64, dtype=float).reshape(8, 8)
    assert np.allclose(dct_2d_homemade(image), dct_2d_fast(image), atol=1e-10)


def test_idct_2d_reconstructs_original_matrix() -> None:
    image = np.arange(64, dtype=float).reshape(8, 8)
    transformed = dct_2d_fast(image)
    reconstructed = idct_2d_fast(transformed)
    assert np.allclose(reconstructed, image, atol=1e-10)


def test_frequency_mask_keeps_only_coefficients_before_diagonal() -> None:
    mask = frequency_keep_mask(block_size=4, cutoff=3)
    expected = np.array(
        [
            [True, True, True, False],
            [True, True, False, False],
            [True, False, False, False],
            [False, False, False, False],
        ]
    )
    assert np.array_equal(mask, expected)
    assert not frequency_keep_mask(block_size=4, cutoff=0).any()
    assert frequency_keep_mask(block_size=4, cutoff=6).sum() == 15


def test_compress_image_array_crops_and_returns_uint8_pixels() -> None:
    image = np.arange(35, dtype=np.uint8).reshape(5, 7)
    original, compressed = compress_image_array(image, block_size=3, cutoff=4)
    assert original.shape == (3, 6)
    assert compressed.shape == (3, 6)
    assert compressed.dtype == np.uint8
    assert compressed.min() >= 0
    assert compressed.max() <= 255


def test_load_original_preview_loads_bmp_before_compression() -> None:
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from PIL import Image

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "preview.bmp"
        Image.fromarray(np.arange(16, dtype=np.uint8).reshape(4, 4)).save(path)

        image, status = load_original_preview(path)

        assert image.shape == (4, 4)
        assert image.dtype == np.uint8
        assert "preview.bmp" in status
        assert "4 x 4" in status


def test_fit_preview_size_keeps_image_inside_available_area() -> None:
    assert fit_preview_size((1000, 500), (400, 160)) == (320, 160)
    assert fit_preview_size((500, 1000), (160, 400)) == (160, 320)
    assert fit_preview_size((100, 50), (400, 300)) == (400, 200)
    assert fit_preview_size((100, 100), (0, 300)) == (1, 1)


def test_compression_preview_keeps_full_original_visible() -> None:
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from PIL import Image

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "not_multiple.bmp"
        Image.fromarray(np.arange(35, dtype=np.uint8).reshape(5, 7)).save(path)

        original_preview, compressed_preview, status = build_compression_preview(path, block_size=3, cutoff=4)

        assert original_preview.shape == (5, 7)
        assert compressed_preview.shape == (3, 6)
        assert "Dimensione originale: 7 x 5 pixel" in status
        assert "Dimensione usata: 6 x 3 pixel" in status


def test_describe_parameter_hints_reports_d_range_under_d_box() -> None:
    f_hint, d_hint = describe_parameter_hints("8", "8", image_shape=(260, 260))
    assert f_hint == "F min 5, max 260"
    assert d_hint == "d da 0 a 14"


def test_describe_parameter_hints_marks_invalid_current_pair() -> None:
    f_hint, d_hint = describe_parameter_hints("4", "9")
    assert f_hint == "F min 6"
    assert d_hint == "d da 0 a 6: ora non valido"


def test_describe_parameter_hints_reports_f_values_from_d() -> None:
    f_hint, d_hint = describe_parameter_hints("", "30", image_shape=(260, 260))
    assert f_hint == "F min 16, max 260"
    assert d_hint == "Inserisci F"


def test_default_benchmark_sizes_cover_large_matrices() -> None:
    assert DEFAULT_SIZES == (8, 16, 32, 64, 128, 256, 512, 768, 1024)


if __name__ == "__main__":
    test_dct_1d_matches_pdf_row_example()
    test_homemade_dct_1d_matches_pdf_row_example()
    test_dct_2d_matches_pdf_block_example()
    test_homemade_dct_2d_matches_fast_dct_2d()
    test_idct_2d_reconstructs_original_matrix()
    test_frequency_mask_keeps_only_coefficients_before_diagonal()
    test_compress_image_array_crops_and_returns_uint8_pixels()
    test_load_original_preview_loads_bmp_before_compression()
    test_fit_preview_size_keeps_image_inside_available_area()
    test_compression_preview_keeps_full_original_visible()
    test_describe_parameter_hints_reports_d_range_under_d_box()
    test_describe_parameter_hints_marks_invalid_current_pair()
    test_describe_parameter_hints_reports_f_values_from_d()
    test_default_benchmark_sizes_cover_large_matrices()
    print("Tutti i test sono passati.")
