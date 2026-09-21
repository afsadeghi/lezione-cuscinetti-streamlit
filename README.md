# Lezione interattiva sui cuscinetti

Prima versione separata dalla lezione sui giunti.

## Avvio locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struttura

- `app.py`: interfaccia e percorso Streamlit.
- `learning_path.py`: contenuti e suggerimenti personalizzati.
- `progress_store.py`: recupero e salvataggio tramite Supabase.
- `assets/video_cuscinetti.mp4`: video iniziale.

Il percorso termina con la scelta di 3, 7 o 14 giorni per la ricerca. L'app calcola la data del prossimo incontro e ricorda allo studente di rientrare con lo stesso codice personale.

Al rientro, il secondo incontro raccoglie in modo guidato: avanzamento, scoperta principale, fonti, fiducia nelle fonti, cambiamento dell'idea iniziale ed eventuale progetto. L'app propone poi una seconda missione orientata al pensiero critico e fissa il terzo incontro.

Il terzo incontro accompagna lo studente a presentare una decisione o un progetto, indicare le prove disponibili, riconoscere un limite, considerare le conseguenze sul sistema e riflettere sulle strategie di apprendimento. Alla fine genera un dossier dei tre incontri senza assegnare voti.

## Supabase su Streamlit Cloud

Usa gli stessi segreti già configurati per l'app sui giunti:

```toml
[supabase]
url = "https://IL-PROGETTO.supabase.co"
anon_key = "LA-CHIAVE-ANON"
```

Questa app applica automaticamente un identificatore separato ai progressi dei cuscinetti. Lo stesso codice personale può quindi essere usato nelle due lezioni senza sovrascrivere il percorso sui giunti.

## Pubblicazione

Carica l'intera cartella in un nuovo repository GitHub e crea una nuova app Streamlit Cloud indicando `app.py` come file principale.
