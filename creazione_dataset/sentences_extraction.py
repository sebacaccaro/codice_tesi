import json
import os
from tqdm import tqdm


class Sentences_Extractor:
    """ Classe che gestisce l'estrazione dal dataset degli archivi vaticani"""
    def __init__(self, dataset_folder: str, langauges: list) -> None:
        """ Costruttore base della classe
        
        Args:
            dataset_folder(`str`): directory nella quale è contenuto il dataset

            laguages(`list(str)`): lista di lingue delle quali si vuole estrarre il testo
         """
        self.dataset_folder = dataset_folder if dataset_folder[
            -1] == "/" else dataset_folder + "/"
        self.languages = langauges
        self.extractSenteces()

    def fileToData(self, filename: str) -> dict:
        """ Funzione di lettura file """
        with open(self.dataset_folder + filename) as f:
            return json.load(f)

    def paragraphListEnriched(self, fileNum: int, paragraphList: list) -> list:
        """ Funzione che dato un file, lo converte in una lista di frasi con delle informazioni aggiuntive 
        
        Args:
            fileNum(`int`): numero del file nel dataset

            paragraphList(`list`): lista dei paragrafi contenuti in un file
        """
        return [{
            "text": p,
            "docnum": fileNum,
            "parId": i,
            "parPos": 0
        } for i, p in enumerate(paragraphList)]

    def extractSenteces(self):
        """ Funzione che estre le frase dai paragrafi """
        fileNames = sorted(list(os.listdir(self.dataset_folder)))

        # Leggendo i files
        files = {
            int(fileName.replace(".json", "")): self.fileToData(fileName)
            for fileName in tqdm(fileNames, "Leggendo i file")
        }
        # Tengo solo quelli nelle lingue scelta
        files = {
            fileNumber: file
            for fileNumber, file in files.items()
            if file["language"] in self.languages
        }
        # Tengo solo i campi paragraph_text e li divido in frasi
        files = {
            fileNumber: file["paragraphs"]
            for fileNumber, file in files.items()
        }

        files = {
            fileNumber: [paragraph["text"] for paragraph in file]
            for fileNumber, file in tqdm(files.items(),
                                         "Dividendo i paragrafi in frasi")
        }

        files = {
            fileNumber: self.paragraphListEnriched(fileNumber, pList)
            for fileNumber, pList in files.items()
        }

        self.files = files

    def saveToFile(self, outfile_name: str) -> None:
        """ Salva le frasi estratte in un file creato con il nome di `outfile_name` """
        print(f"Salvando le frasi in {outfile_name}...")
        with open(outfile_name, "w") as f:
            json.dump(self.files, f, indent=2)
        print(f"{outfile_name} scritto con successo ;)")

    def get_extracted_sentences(self) -> dict:
        """ Lista delle frasi estratte """
        return self.files


def main() -> None:
    extr = Sentences_Extractor("../../Tesi/Dataset/vatpub", ["it"])
    extr.saveToFile("out.json")
    print(extr.get_extracted_sentences()[5])


if __name__ == "__main__":
    main()
