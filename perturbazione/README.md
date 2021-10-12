# Perturbazione
Questa cartella contiene tutti gli script che servono a definire la perturbazione del testo.


Gli script in questa directory non vanno lanciati, in quanto esportano classi e funzioni usate in altre parti del progetto. Fa eccezzione `error_matrix_extraction.py` che serve per creare la matrice degli errori.

## pipeline.py
Il file contiene:
- La classe base ```PertubationModule``` che definisce il template per creare tutti i moduli di perturbazione.
- Delle funzioni stile "factory" per creare più facilmente delle istanze di moduli di pertubazione che modellano diversi errori.
- La classe ```Pipeline``` che combina vari moduli di perturbazione per applicarli in serie sul testo da perturbare.
- La classe ```SuperPipeline``` che combina varie pipeline per perturbare lunghi segmenti di testo in modo etorogeneo.

## pipelines_def.py
Il file contiene delle funzioni helper per creare delle pipeline di diverso tipo (segmentazione, token, misto).

## perturbation_superpipelines.py
Il file definisce le SuperPipeline (`T1`,`T2`,`T3`,`S1`,`S2`,`S3`,`M1`,`M2`,`M3`,) usate per i test sperimentali

**Per funzionare correttamente, il file error_matrix.json deve essere presente in questa directory**

## error_matrix_extraction.json
Data una lista di correzioni, crea la matrice degli errori nel file `error_matrix.json`. A scopo di esempio, viene fornito il file `correction_examples.json` che contine una lista di correzioni.