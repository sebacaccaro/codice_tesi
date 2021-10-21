""" Main di esempio per l'estrazione delle frasi e dei sample dal dataset vaticano """
from sentences_extraction import Sentences_Extractor
from sample_extraction import Sample_Extractor


def main() -> None:
    sent_extr = Sentences_Extractor("../../Tesi/Dataset/vatpub", ["it"])
    sentences = sent_extr.get_extracted_sentences()
    # Limite settato a 40 chiavi per evitare di andare avanti per troppo tempo
    # Togliere l'if per un'esecuzione utile
    sentences = {k: v for k, v in sentences.items() if k < 40}

    sample_extr = Sample_Extractor(sentences, 50, 100)
    sample_extr.extract()
    sample_extr.saveToFile("samples.json")


if __name__ == "__main__":
    main()
