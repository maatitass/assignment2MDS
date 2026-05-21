# Assignment 2 - Compressione immagini tramite DCT

Progetto Python semplice per il secondo assignment di Metodi del Calcolo
Scientifico. Il codice implementa:

- DCT2 fatta in casa con matrice ortonormale esplicita, come nei file MATLAB del professore;
- DCT2 fast tramite `scipy.fft`;
- compressione di immagini BMP in scala di grigi tramite taglio delle frequenze;
- GUI minimale per scegliere immagine, `F` e `d`.

La relazione formale e' fuori scope per ora: questo README e' solo operativo.

## Dipendenze

Usare un ambiente locale, senza installazioni globali:

```bash
uv venv
uv pip install -r requirements.txt
```

## Test

```bash
uv run python test_assignment.py
```

I test controllano i due blocchi numerici del PDF, il confronto tra DCT2 fatta
in casa e DCT2 fast, la IDCT2, la maschera `k + ell >= d` e la compressione di
una piccola immagine.

## Benchmark ed esempi

```bash
uv run python run_assignment.py
```

Output principali:

- `results/benchmark.csv`
- `results/benchmark_dct2.png`
- `results/examples/*_comparison.png`
- `results/examples/*.bmp`

Il benchmark standard usa:

```text
N = 8, 16, 32, 64, 128, 256, 512, 768, 1024
```

Per usare dimensioni specifiche nel benchmark:

```bash
uv run python run_assignment.py --size 16 --size 32 --size 64
```

Per comprimere una immagine specifica:

```bash
uv run python run_assignment.py --image immagini/320x320.bmp --block-size 8 --cutoff 8
```

Il parametro `F` e' la dimensione dei blocchi quadrati. Il parametro `d` deve
rispettare:

```text
0 <= d <= 2F - 2
```

I coefficienti eliminati sono quelli con indice `k + ell >= d`, usando indici
che partono da zero.

## GUI

```bash
uv run python gui.py
```

La GUI permette di scegliere un file `.bmp`, inserire `F` e `d`, e vedere
subito l'immagine originale selezionata con la sua dimensione. Dopo aver
premuto `Comprimi`, mostra affiancate l'immagine originale intera e quella
ricostruita sui blocchi completi usati dalla DCT2. Le due anteprime vengono
ridimensionate dentro la finestra senza tagliare l'immagine.

Sotto le caselle `F` e `d` la GUI mostra anche i valori ammessi:

- sotto `F`, dato `d`, indica il minimo `F` necessario;
- sotto `d`, dato `F`, indica il range valido per `d`;
- se un'immagine e' selezionata, indica anche il massimo `F` possibile per
  avere almeno un blocco completo.

Se `F` non divide esattamente larghezza o altezza, il risultato compresso usa
solo la parte dell'immagine coperta da blocchi completi, come richiesto dal
testo del progetto. La GUI lascia comunque visibile l'immagine originale intera
a sinistra e indica in basso la dimensione effettivamente usata per la DCT2.

## Struttura

- `dct_utils.py`: funzioni DCT, IDCT, maschera frequenze e compressione;
- `run_assignment.py`: benchmark DCT2 e generazione esempi;
- `gui.py`: interfaccia Tkinter minimale;
- `test_assignment.py`: test veloci senza framework esterni;
- `immagini/`: immagini BMP fornite dal docente.
