# Style card — guida di replica dello stile (agnostica al contenuto)

> Prompt prescrittivo per replicare lo stile di scrittura delle relazioni del corso
> "Metodi del Calcolo Scientifico". Incollabile direttamente come istruzione a un'AI,
> insieme al contenuto da scrivere. Non è una linea guida generica: ogni regola è un vincolo.

---

## 1. Identità e voce
- Voce dominante: **prima persona plurale** ("noi" autoriale) per ogni **scelta** o **azione**
  compiuta: *abbiamo implementato, abbiamo sfruttato, ci siamo affidati, abbiamo evitato,
  abbiamo condotto, la nostra intuizione è che…*
- Voce **impersonale/passiva** riservata a **procedure e misure** oggettive: *il confronto è
  stato eseguito su…, per ogni N si è preso il tempo minimo…, sono stati salvati…*.
- **Regola di alternanza**: quando racconti una decisione → "noi"; quando riporti un protocollo
  o un dato → impersonale. Non mescolarle nella stessa frase.
- Mai prima persona singolare. Mai tono divulgativo-entusiasta. Mai impersonale freddo
  dall'inizio alla fine.

## 2. Architettura del paragrafo (obbligatoria)
Ogni unità argomentativa segue questo arco a 4 tempi:
1. **Premessa/ipotesi teorica**: dichiara cosa ci si aspetta e perché. Aperture tipiche:
   *"Un principio centrale è…", "Da un punto di vista teorico…", "ci si aspetta che…",
   "è prevedibile che…"*.
2. **Evidenza** (dato/figura/tabella) introdotta in modo neutro: *"I risultati sono mostrati
   nella Figura~X", "I tempi misurati sono riportati nella Tabella~Y"*.
3. **Verifica esplicita dell'ipotesi**, tornando alla premessa: *"I risultati confermano questa
   ipotesi in maniera esemplare", "L'osservazione dei risultati conferma queste premesse",
   "Questo comportamento convalida il nostro assunto di partenza"*.
4. **Spiegazione del meccanismo + chiusura** che colloca il caso in un quadro più ampio:
   *"Questo si verifica poiché…", "Ci troviamo di fronte alla situazione opposta…"*.

## 3. Meccanica della frase
- **Periodi articolati**, in media 2–4 proposizioni, aperti spesso da un complemento o gerundio:
  *"Partendo dalla teoria…", "Per estendere questo concetto…", "Avendo a disposizione D…",
  "Trattandosi di due moltiplicazioni…"*.
- Dopo 1–2 frasi lunghe, **una frase corta che sintetizza o contrappone**: *"La DCT è l'operatore
  ideale.", "Ci troviamo di fronte alla situazione opposta."*
- **Costruzioni causali e contrastive ricorrenti**:
  - *Poiché X, Y.* / *Trattandosi di X, Y.* / *Dato X, Y.*
  - *non X, ma Y* ("non è concentrata, ma risulta distribuita su un ampio spettro").
  - struttura a specchio *dove… dove…* ("dove quest'ultimo concentrava lo spettro nelle basse
    frequenze, la scacchiera lo addensa in quelle alte").
- **Hedge + asserzione** per le intuizioni: *"La nostra intuizione è che questo fenomeno dipenda
  da…"* (congiuntivo dopo l'ipotesi).

## 4. Inventario di connettivi (frequenza alta)
*Di conseguenza · Pertanto · Poiché · In altri termini · Tuttavia · In particolare · Ad esempio ·
Infatti · Invece · Nello specifico · Inoltre · A parità di · Al contrario.*
Apri molte frasi con un connettivo o un complemento, raramente con il soggetto nudo.

## 5. Palette lessicale (parole-firma da preferire)
- Valutazioni qualificate: *trascurabile, marcato (degrado), severo, esemplare / in maniera
  esemplare, agilmente (supera agilmente), nettamente (superiore), degno di nota, soddisfacente,
  sostanzialmente inalterato.*
- Sostantivi-quadro: *premessa, assunto di partenza, quadro coerente, comportamento, andamento,
  scenario (ideale/opposto), fenomeno.*
- Verbi attivi precisi: *azzerare, tagliare, scartare (preventivamente), concentrare,
  contestualizzare, abbattere (il costo), delegare, restituire, convalidare.*
- **Termini tecnici inglesi lasciati in originale e marcati in corsivo** (`\emph{}`/`\textit{}`):
  *fast, wrapper, overhead, filesystem*. Non tradurli forzatamente.
- **Concetti chiave enfatizzati alla prima occorrenza** in `\emph{}`, poi liberi.

## 6. Trattamento di numeri e risultati (rigido)
- **Nessun numero nudo**: ogni valore è seguito da una lettura qualitativa. Modello: *"il PSNR
  supera agilmente i $54$~dB, restituendo una ricostruzione visivamente indistinguibile"*.
- **Criteri/soglie dichiarati prima** di interpretare, in elenco con `\textbf{}` sulla soglia.
- **Confronto teoria↔pratica** come motivo ricorrente: previsione formale messa a fronte della
  misura ("L'andamento sperimentale rispetta le predizioni teoriche").
- Esempi numerici introdotti con *"Ad esempio, impostando … si raggiungono …, superando …"*.

## 7. Convenzioni tipografiche (LaTeX)
- Tutto in math mode anche inline: variabili `$F$, $d$, $N$`, complessità `$O(N^3)$`, percentuali
  `$5\%$`, unità con tilde `$54$~dB`.
- **Tilde non-breaking** prima di riferimenti e unità: `Figura~\ref{}`, `Tabella~\ref{}`,
  `$10$~dB`.
- `\emph{}` = termine-concetto; `\textbf{}` = lead-in di elenco e soglie; `\texttt{}` = ogni
  identificatore/nome di file/funzione/libreria.
- Virgolette: caporali `\guillemotleft … \guillemotright` per citazioni nel testo; doppi apici
  dritti `"…"` per uso connotativo ("liscia"); `` ``---'' `` per trattini citati.
- Trattino `--` per incisi e intervalli; elenchi `itemize`/`enumerate` solo per **passi
  procedurali, criteri o enumerazioni**, mai per argomentare.

## 8. Divieti (per non uscire dallo stile)
- ✗ Frasi-slogan, entusiasmo, esclamazioni.
- ✗ Elenchi puntati al posto della prosa argomentativa.
- ✗ Numeri senza commento; affermazioni senza il "perché".
- ✗ Prima persona singolare; impersonale uniforme.
- ✗ Frasi tutte corte e paratattiche (stile "soggetto-verbo-complemento" ripetuto).

## 9. Esempio di pastiche (tema neutro, per calibrare il modello)
> Per valutare l'efficienza dell'ordinamento, abbiamo posto a confronto diretto la nostra
> implementazione *naïve* con quella offerta dalla libreria standard. Da un punto di vista teorico,
> ci si aspetta che il costo cresca come $O(n\log n)$: poiché l'algoritmo suddivide
> ricorsivamente l'input, il numero di confronti si concentra nei livelli più alti dell'albero di
> ricorsione. I tempi misurati sono riportati nella Tabella~\ref{tab:sort}. I risultati confermano
> questa ipotesi in maniera esemplare: a partire da $n=10^4$ le curve si separano nettamente e la
> versione di libreria si mantiene agilmente sotto il millisecondo. Ad esempio, per $n=10^6$ il
> nostro prototipo richiede $1.8$~s contro i $0.12$~s della libreria, un divario di circa quindici
> volte. Questo comportamento convalida il nostro assunto di partenza: l'*overhead* dell'interprete
> penalizza i cicli espliciti, mentre l'implementazione ottimizzata delega il lavoro a codice
> compilato.

---

### Uso rapido
Passa a un'AI: **questo file** + *"Scrivi la sezione X seguendo esattamente questo stile"* +
il contenuto/dati. La style card vincola voce, ritmo, connettivi e convenzioni tipografiche.
