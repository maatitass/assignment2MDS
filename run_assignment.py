"""Command line runner for the second MCS assignment."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dct_utils import (
    compress_image_array,
    dct_2d_fast,
    dct_2d_homemade,
    load_bmp_grayscale,
    save_grayscale_image,
    time_function,
)


DEFAULT_SIZES = (8, 16, 32, 64, 128, 256, 512, 768, 1024)
DEFAULT_EXAMPLE_IMAGES = ("80x80.bmp", "160x160.bmp", "320x320.bmp", "prova.bmp", "shoe.bmp")


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    output_dir = args.output
    if not output_dir.is_absolute():
        output_dir = base_dir / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    sizes = args.size if args.size else list(DEFAULT_SIZES)
    benchmark_rows = run_benchmark(sizes, args.repeats)
    benchmark_csv = output_dir / "benchmark.csv"
    write_benchmark_csv(benchmark_rows, benchmark_csv)
    plot_path = output_dir / "benchmark_dct2.png"
    plot_benchmark(benchmark_rows, plot_path)

    print(f"Benchmark scritto in: {benchmark_csv}")
    print(f"Grafico benchmark scritto in: {plot_path}")

    if args.examples:
        image_paths = resolve_images(args.image, base_dir)
        example_dir = output_dir / "examples"
        example_dir.mkdir(parents=True, exist_ok=True)
        for image_path in image_paths:
            original, compressed = compress_image_array(
                load_bmp_grayscale(image_path),
                block_size=args.block_size,
                cutoff=args.cutoff,
            )
            compressed_path = example_dir / f"{image_path.stem}_F{args.block_size}_d{args.cutoff}.bmp"
            comparison_path = example_dir / f"{image_path.stem}_F{args.block_size}_d{args.cutoff}_comparison.png"
            save_grayscale_image(compressed_path, compressed)
            save_comparison(original, compressed, comparison_path, image_path.name, args.block_size, args.cutoff)
            print(f"Esempio scritto in: {compressed_path}")
            print(f"Confronto scritto in: {comparison_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compressione immagini tramite DCT2")
    parser.add_argument(
        "--size",
        action="append",
        type=int,
        help="Dimensione N per benchmark N x N. Ripetibile. Default: 8,16,32,64,128,256,512,768,1024.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Ripetizioni per ogni timing. Si prende il tempo migliore. Default: 3.",
    )
    parser.add_argument(
        "--image",
        action="append",
        type=Path,
        help="Immagine .bmp per gli esempi. Ripetibile. Default: alcune immagini in immagini/.",
    )
    parser.add_argument("--block-size", type=int, default=8, help="Ampiezza F dei blocchi. Default: 8.")
    parser.add_argument("--cutoff", type=int, default=8, help="Soglia d delle frequenze. Default: 8.")
    parser.add_argument("--output", type=Path, default=Path("results"), help="Cartella output. Default: results.")
    parser.add_argument("--no-examples", dest="examples", action="store_false", help="Esegue solo il benchmark.")
    parser.set_defaults(examples=True)
    return parser.parse_args()


def run_benchmark(sizes: list[int], repeats: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    rng = np.random.default_rng(0)
    for size in sizes:
        image = rng.integers(0, 256, size=(size, size)).astype(float)
        homemade_time = time_function(dct_2d_homemade, image, repeats=repeats)
        fast_time = time_function(dct_2d_fast, image, repeats=repeats)
        rows.append(
            {
                "N": str(size),
                "homemade_seconds": f"{homemade_time:.8f}",
                "fast_seconds": f"{fast_time:.8f}",
            }
        )
        print(f"N={size:4d} homemade={homemade_time:.6f}s fast={fast_time:.6f}s")
    return rows


def write_benchmark_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["N", "homemade_seconds", "fast_seconds"])
        writer.writeheader()
        writer.writerows(rows)


def plot_benchmark(rows: list[dict[str, str]], path: Path) -> None:
    sizes = [int(row["N"]) for row in rows]
    homemade = [float(row["homemade_seconds"]) for row in rows]
    fast = [float(row["fast_seconds"]) for row in rows]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(sizes, homemade, marker="o", label="DCT2 fatta in casa")
    ax.semilogy(sizes, fast, marker="o", label="DCT2 fast SciPy")
    ax.set_xlabel("N")
    ax.set_ylabel("Secondi")
    ax.set_title("Confronto tempi DCT2")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_comparison(
    original: np.ndarray,
    compressed: np.ndarray,
    path: Path,
    image_name: str,
    block_size: int,
    cutoff: int,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(original, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title("Originale ritagliata")
    axes[1].imshow(compressed, cmap="gray", vmin=0, vmax=255)
    axes[1].set_title(f"Compressa F={block_size}, d={cutoff}")
    for axis in axes:
        axis.axis("off")
    fig.suptitle(image_name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def resolve_images(paths: list[Path] | None, base_dir: Path) -> list[Path]:
    if paths:
        resolved = []
        for path in paths:
            if not path.is_absolute():
                path = base_dir / path
            if not path.exists():
                raise FileNotFoundError(f"Immagine non trovata: {path}")
            resolved.append(path)
        return resolved

    data_dir = base_dir / "immagini"
    resolved = [data_dir / name for name in DEFAULT_EXAMPLE_IMAGES if (data_dir / name).exists()]
    if not resolved:
        raise FileNotFoundError(f"Nessuna immagine di esempio trovata in: {data_dir}")
    return resolved


if __name__ == "__main__":
    main()
