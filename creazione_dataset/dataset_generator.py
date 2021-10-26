from tqdm import tqdm
import json
import sys
import nltk
from random import shuffle

sys.path.insert(0, "../perturbazione/")
from perturbation_superpipelines import sup_pipelines

nltk.download('punkt')


class Dataset_Generator:
    """ Classe che si occupa di creare un dataset con vari livelli di perturbazione a partire da un lista di sample """
    def __init__(self, datset_filename: str) -> None:
        """ Costruttore base della classe
        
        Args:
            dataset_filename(`str`): nome del file in cui si trovano i samples
        """
        print("Caricando le frasi estratte...")
        with open(datset_filename) as f:
            self.dataset = json.load(f)
        self.dataset = [{**d, "perturbed": {}} for d in self.dataset]

    def filter_paragraphs(self) -> None:
        """ Funzione che si occupa di filtrare tutti i sample del dataset.
        
        Tutti i sample in `self.dataset` appartenenti al primo o all'ultimo paragrafo di un documento sono scartati
        """
        print("Filtrando primi e ultimi paragrafi")

        def isFirstParagraph(fragment: dict) -> bool:
            return fragment["parId"] == 0

        def isLastParagraph(fragment: dict, maxes: dict) -> bool:
            return fragment["parId"] == maxes[fragment["docnum"]]

        maxes = {}
        for fragment in self.dataset:
            if fragment["docnum"] not in maxes:
                maxes[fragment["docnum"]] = []
            maxes[fragment["docnum"]].append(fragment["parId"])
        maxes = {
            docnum: max(maxList)
            for docnum, maxList in tqdm(maxes.items())
        }
        self.dataset = [
            f for f in tqdm(self.dataset)
            if not (isFirstParagraph(f) or isLastParagraph(f, maxes))
        ]

    def perturbed_sample(self, sample: dict, perturbed: str,
                         sup_name: str) -> dict:
        """ Aggiunge una frase perturbata al campo `perturbed` di un sample. Restituisce il nuovo sample
        
        Args:
            sample(`dict`): il sample che è stato perturbato
            perturbed(`str`): frase già perturbata
            sup_name(`str`): nome della pipeline di perturbazione utlizzata
        """
        return {
            **sample, "perturbed": {
                **sample["perturbed"], sup_name: perturbed
            }
        }

    def perturb_samples(self,
                        reducedDimension: int = None,
                        filter_paragraphs: bool = True) -> None:
        """ Funzione che si occupa del processo di perturbazione del dataset 
        
        Args:
            reducedDimension(`int`): se si vuole perturbare e tenere solo un certo numero di sample, questo parametro indica il numero di sample da tenere
            filter_paragraphs(`bool`): se False, la fase di filraggio degli ultimi paragrafi non viene applicata. Di default è True.            
        """
        reducedDimension = reducedDimension if reducedDimension and reducedDimension < len(
            self.dataset) else len(self.dataset)
        i = 0
        if filter_paragraphs:
            self.filter_paragraphs()
        for sup_name, sup in sup_pipelines.items():
            desc = f"Perturbando con {sup_name} ({i}/{len(sup_pipelines)})"
            i += 1
            self.dataset = [
                self.perturbed_sample(s, sup.run(s["text"]), sup_name)
                for s in tqdm(self.dataset[:reducedDimension], desc=desc)
            ]
        shuffle(self.dataset)

    def saveToFile(self, filename: str, reducedDimension: int = None):
        """ Salva su file json il dataset perturbato. Prima di eseguirlo è necessario eseguire il metodo `perturb_dataset` 
        
        Args:
            filename(`str`): nome del file in cui salvare il dataset
            reducedDimension(`int`): se impostato, indica quanti sample perturbati sono salvati        
        """
        reducedDimension = reducedDimension if reducedDimension and reducedDimension < len(
            self.dataset) else len(self.dataset)
        print(
            f"Salvando {reducedDimension} frasi con perturbazioni in {filename}..."
        )
        with open(filename, "w") as f:
            json.dump(self.dataset[:reducedDimension], f, indent=2)


def main():
    dst_get = Dataset_Generator("./samples.json")
    dst_get.perturb_samples(3000)
    dst_get.saveToFile("dataset.json")
    dst_get.saveToFile("dataset_reduced.json", 1000)


if __name__ == "__main__":
    main()