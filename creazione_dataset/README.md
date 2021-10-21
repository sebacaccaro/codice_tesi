# CREAZIONE DATASET
In questa cartella sono contenunti tutti gli script necessari per estrarre le frasi dal dataset degli archivi vaticani e trasformale in un dataset con frasi perturbate.

## sentences_extraction.py
Esporta la classe `Sentences_Extractor` che si occupa dell'estrazione delle frasi dai dataset vaticani

## sample_extraction.py
Esporta la classe `Samples_Extractor` che si occupa dell'estrazione dei sample dalle frasi estratte dal `Sentences_Extractor`

## sample_extraction.py
Main di esempio con le classi `Sentences_Extractor` e `Samples_Extractor`  l'estrazione dei sample dal dataset. L'esecuzione è limitata a pochi documenti, nel file sono presenti dei commenti che spiegano come farlo funzionare su tutti i docs.

## samples.json
Esempio ridotto dell'output del processo di estrazione dei samples.