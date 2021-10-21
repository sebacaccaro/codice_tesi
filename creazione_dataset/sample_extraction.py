from re import finditer
import json
from itertools import chain
import sys

sys.path.insert(0, "../utils/")
from utils import find_all


class Sample_Extractor:
    """ Classe che gestisce l'estrazione e la creazione di campioni a partire dalla lista delle frasi """
    def __init__(self,
                 sentences: list,
                 sentences_min_len=8,
                 sentences_max_len=100) -> None:
        """ Costruttore base della classe
        
        Args:
            senteces(`list`): list of extracted sentences
            sentences_min_len (int): minum lenght of a sentence after elaboration
            sentences_max_len (int): maximum lenght of a sentence ater elaboration
        """
        self.sentences = {int(key): value for key, value in sentences.items()}
        self.doc_min = 0
        self.doc_max = max(sentences.keys())
        self.min_len = sentences_min_len
        self.max_len = sentences_max_len

    def fallbackSplit(self, sentence, max_optimal_size):
        """ Seconda strategia di split di fallback """
        """ Chop of the sentece string in string of max_optimal_size and the rest """
        if len(sentence["text"]) <= max_optimal_size:
            return sentence, None
        return {
            **sentence, "text": sentence["text"][:max_optimal_size]
        }, {
            **sentence, "text": sentence["text"][max_optimal_size:],
            "parPos": sentence["parPos"] + 1
        }

    def spaceSplit(self, sentence, max_optimal_size):
        """ Strategia di split di fallback """
        if (len(sentence["text"]) <= max_optimal_size):
            return sentence, None
        punktMarks = [" "]
        splitPoints = [
            find_all(sentence["text"], punktMark) for punktMark in punktMarks
        ]
        splitPoints = list(chain(*splitPoints))
        if all([x == -1 or x >= max_optimal_size for x in splitPoints]):
            return self.numSplit(sentence, max_optimal_size)
        splitPoint = sorted([x for x in splitPoints if x <= max_optimal_size
                             ])[-1] + 1
        return {
            **sentence, "text": sentence["text"][:splitPoint]
        }, {
            **sentence, "text": sentence["text"][splitPoint:],
            "parPos": sentence["parPos"] + 1
        }

    def smartSplit(self, sentence, max_optimal_size):
        """ Divide the string into a optimal dataset string and the rest

        Parameters:
        sentece (str): sentece to be split
        max_optimal_size (int): upper limit for return lenght, and optimal size to reach

        Returns:
        optimal_str (str): optimal string to be added to the dataset
        rest_str (str): rest of the string
        """
        if (len(sentence["text"]) <= max_optimal_size):
            return sentence, None
        punktMarks = ["?", "!", ";", ":"]
        splitPoints = [
            find_all(sentence["text"], punktMark) for punktMark in punktMarks
        ]
        splitPoints = list(chain(*splitPoints))
        if all([x == -1 or x >= max_optimal_size for x in splitPoints]):
            return self.spaceSplit(sentence, max_optimal_size)
        splitPoint = sorted([x for x in splitPoints if x <= max_optimal_size
                             ])[-1] + 1
        return {
            **sentence, "text": sentence["text"][:splitPoint]
        }, {
            **sentence, "text": sentence["text"][splitPoint:],
            "parPos": sentence["parPos"] + 1
        }

    def accettable_length(self, sent: str):
        """ Returns true if the sentece is within the accetable lenght range """
        return self.min_len <= len(sent) <= self.max_len

    def extract(self) -> None:
        """ Performa l'estrazione dei sample dalle frasi """
        allsentences = list(chain(*self.sentences.values()))
        sent_number = len(allsentences)
        extracted = [
            phr for phr in allsentences if self.accettable_length(phr["text"])
        ]

        allsentences = [
            phr for phr in allsentences
            if not self.accettable_length(phr["text"])
        ]

        print(f"Numero totali di frasi nel dataset: {sent_number}")
        print(f"Splittando frasi in sequenze da max {self.max_len} caratteri")

        while len(allsentences) > 0:
            if len(extracted) % 1000 == 0:
                print(
                    f"Frasi da elaborare: {len(allsentences)} -- Frasi Prodotte: {len(extracted)}"
                )
            extracted_sent, rest = self.smartSplit(allsentences.pop(0),
                                                   self.max_len)
            extracted.append(extracted_sent)
            if (rest):
                allsentences.append(rest)

        self.extracted = [
            x for x in extracted if self.accettable_length(x["text"])
        ]

    def getSamples(self) -> list:
        """ Ritorna tutti i sample estratti """
        return self.extracted

    def saveToFile(self, output_filename: str) -> None:
        "Salva le frasi estratte su file"
        with open(output_filename, "w") as f:
            json.dump(self.extracted, f, indent=2)