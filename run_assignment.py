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
    frequency_keep_mask,
    load_bmp_grayscale,
    save_grayscale_image,
    time_function,
)


DEFAULT_SIZES = (8, 16, 32, 64, 128, 256, 512, 768, 1024)


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
        
        combinations = [
            (8, 2), (8, 5), (8, 8), (8, 14),
            (16, 4), (16, 10), (16, 20), (16, 30),
            (32, 8), (32, 20), (32, 40), (32, 60),
        ]
        
        for image_path in image_paths:
            print(f"\nElaborazione di: {image_path.name}")
            original = load_bmp_grayscale(image_path)
            
            compressions = []
            metrics = []
            
            for f, d in combinations:
                if f > original.shape[0] or f > original.shape[1]:
                    print(f"  Salto F={f}, d={d}: blocco più grande dell'immagine {original.shape}")
                    continue

                cropped_original, compressed = compress_image_array(
                    original,
                    block_size=f,
                    cutoff=d,
                )
                
                mse, psnr = calculate_metrics(cropped_original, compressed)
                comp_ratio = calculate_compression_ratio(f, d)
                
                compressions.append((f, d, compressed, psnr))
                metrics.append({
                    "F": f,
                    "d": d,
                    "mse": float(mse),
                    "psnr": float(psnr),
                    "compression_ratio": float(comp_ratio)
                })
                
            if not compressions:
                print(f"Nessuna compressione valida generata per {image_path.name}. Salto i grafici.")
                continue

            grid_path = example_dir / f"{image_path.stem}_grid.png"
            plots_path = example_dir / f"{image_path.stem}_metrics_plot.png"
            csv_path = example_dir / f"{image_path.stem}_metrics.csv"
            
            save_compression_grid(compressions, grid_path, image_path.name)
            save_informative_plots(metrics, plots_path, image_path.name)
            write_image_metrics_csv(metrics, csv_path)
            
            print(f"Grid salvata in: {grid_path}")
            print(f"Grafici salvati in: {plots_path}")
            print(f"CSV salvato in: {csv_path}")


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
        help="Immagine .bmp per gli esempi. Ripetibile. Default: tutte le immagini .bmp in immagini/.",
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


def calculate_metrics(original: np.ndarray, compressed: np.ndarray) -> tuple[float, float]:
    mse = np.mean((original.astype(float) - compressed.astype(float)) ** 2)
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(255.0 / np.sqrt(mse))
    return float(mse), float(psnr)


def calculate_compression_ratio(block_size: int, cutoff: int) -> float:
    mask = frequency_keep_mask(block_size, cutoff)
    return float(np.count_nonzero(mask) / (block_size * block_size))


def save_compression_grid(
    compressions: list[tuple[int, int, np.ndarray, float]],
    path: Path,
    image_name: str,
) -> None:
    n_compressions = len(compressions)
    cols = min(n_compressions, 4)
    rows = (n_compressions + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.5, rows * 3.5))
    axes = np.atleast_1d(axes).flatten()
    
    for i, (f, d, comp_img, psnr) in enumerate(compressions):
        ax = axes[i]
        ax.imshow(comp_img, cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"F={f}, d={d}\nPSNR: {psnr:.2f} dB")
        ax.axis("off")
        
    for j in range(n_compressions, len(axes)):
        axes[j].axis("off")
        
    fig.suptitle(f"Grid di compressioni per: {image_name}")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_informative_plots(metrics: list[dict], path: Path, image_name: str) -> None:
    f_values = sorted(list(set(m["F"] for m in metrics)))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Plot 1: PSNR vs d (linee raggruppate per F)
    # Plot 2: PSNR vs percentuale di coefficienti mantenuti (linee per F)
    for f in f_values:
        data_f = [m for m in metrics if m["F"] == f]
        data_f.sort(key=lambda x: x["d"])

        ds = [m["d"] for m in data_f]
        ratios = [m["compression_ratio"] * 100 for m in data_f]
        psnrs = [m["psnr"] for m in data_f]

        ax1.plot(ds, psnrs, marker="o", label=f"F={f}")
        ax2.plot(ratios, psnrs, marker="s", label=f"F={f}")

    ax1.set_xlabel("Soglia di frequenza (d)")
    ax1.set_ylabel("PSNR (dB)")
    ax1.set_title("PSNR vs d")
    ax1.grid(True, linestyle="--", linewidth=0.5)
    ax1.legend()

    ax2.set_xlabel("% coefficienti mantenuti")
    ax2.set_ylabel("PSNR (dB)")
    ax2.set_title("PSNR vs Tasso di Compressione")
    ax2.grid(True, linestyle="--", linewidth=0.5)
    ax2.legend()
    
    fig.suptitle(f"Analisi metriche: {image_name}")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def write_image_metrics_csv(metrics: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["F", "d", "mse", "psnr", "compression_ratio"])
        writer.writeheader()
        writer.writerows(metrics)


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
    if not data_dir.exists() or not data_dir.is_dir():
        raise FileNotFoundError(f"Cartella immagini non trovata: {data_dir}")
        
    resolved = sorted(list(data_dir.glob("*.bmp")))
    if not resolved:
        raise FileNotFoundError(f"Nessuna immagine .bmp trovata in: {data_dir}")
    return resolved


if __name__ == "__main__":
    main()
