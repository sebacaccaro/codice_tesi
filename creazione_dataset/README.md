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

## dataset_generator.py
Esporta la classe `Dataset_Generator` che si occupa della creazione (con perturbazione) del dataset usato testare la correzione. Nel file è presente anche un main di esempio che ne mostra l'utilizzo.

## dataset.json e dataset_reduced.json
Dataset di esempio creati attraverso la classe `Dataset_Generator`. Sono rispettivamente una versione completa e ridotta dello stesso dataset, creati con il main di `dataset_generator.py`. Entrambi comunque sono molto brevi e a solo scopo di esempio: per utilizzarli per test reali si consiglia di creare versioni più amplie.