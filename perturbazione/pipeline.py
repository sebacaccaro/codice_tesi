from abc import abstractmethod
import sys
from typing import List

sys.path.insert(0, "../utils/")
from utils import probability_boolean, find_all, randint, shuffle, random_choice, weighted_choice
from itertools import chain
from nltk import word_tokenize
from detokenize import detokenize


class PerturbationModule:
    """ Modulo di perturbazione base. Il suo funzionamento è dato dalla funzione di perturbazione base fornita nel costruttore """
    def __init__(self, perturbation_function: function, token_grouping: int,
                 probability: float) -> None:
        """ Costruttore base della classe
        
        Args:
            pertubation_function(:obj:`function`): funzione che prende un gruppo di token di lunghezza stabilita dal parametro :obj:`token_grouping` e li perturba

            token_grouping:(:obj:`int`): numero di token che la funzione di perturbazione prende in gruppo per la perturbazione

            probability(:obj:`float`): probabilità da 0 a 1 che la funzione di perturbazione perturbi un certo gruppo di token
         """
        self.perturbation_function = perturbation_function
        self.token_grouping = token_grouping
        self.probability = probability

    def group(self, tokens: list) -> list:
        """ Funzione che prende in input una lista di token e li ritorna raggruppati in gruppi da :obj:`self.token_grouping` tokens
        
        Args:
            tokens:(:obj:`list(str)`): lista di token da raggruppare
        """
        grouped = []
        current = []
        for t in tokens:
            if len(current) == self.token_grouping:
                grouped.append(current)
                current = []
            current.append(t)
        if len(current) > 0:
            grouped.append(current)
        return grouped

    def apply(self, tokens: list) -> list:
        """ Funzione che prende in input una lista di token e applica la funzione di perturbazione  :obj:`self.perturbation_function`
        
        Args:
            tokens: lista di token da perturbare
        """
        perturbed_list = [
            self.perturbation_function(t)
            if probability_boolean(self.probability)
            and len(t) == self.token_grouping else t
            for t in self.group(tokens)
        ]
        return list(chain.from_iterable(perturbed_list))


class TokenizerModule:
    """ Modulo che si occupa della tokenizzazione """
    def apply(self, input: str) -> list:
        """ Funzione che tokenizza la stringa data in input 
        
        Args:
            input(:obj:`str`): stringa da tokenizzare
        """
        return word_tokenize(input)


class DetokenizerModule:
    """ Modulo che si occupa della detokenizzazione """
    def apply(self, input: list) -> str:
        """ Funzione che detokenizza i token dati in input, ricomponendo una frase
        
        Args:
            input(:obj:`list(str)`): lista di token da detokenizzare
        """
        return detokenize(input)


def split(token: str) -> str:
    """ Funzione spezzetta un token aggiungendo spazi fra le lettere """
    return " ".join([char for char in token])


def split_tokens(list_of_tokens: list) -> list:
    """ Funzione ausiliare di `SplitModuleGenerator` """
    return [split(t) for t in list_of_tokens]


def SplitModuleGenerator(probability: float) -> PerturbationModule:
    """ Funzione che genera moduli di split che perturbano con una probabilità di `probability` 
    Un modulo di split è un modulo che intermezza le lettere di una parola con degli spazi
    """
    return PerturbationModule(perturbation_function=split_tokens,
                              token_grouping=1,
                              probability=probability)


def AddPunctuationModule(probability: float,
                         punctChar: str) -> PerturbationModule:
    """ Funzione che genera moduli di aggiunta di punteggiatura spuria.
    Un modulo di aggiunta punteggiatura spuria inserisce un carattere :obj:`punctChar` dopo un token con proabilità :obj:`probability`"""
    return PerturbationModule(
        perturbation_function=lambda tokens: [*tokens, punctChar],
        token_grouping=1,
        probability=probability)


def MergeWordHyphenModule(probability: float) -> PerturbationModule:
    """ Funzione che genera moduli che uniscono due parole con un trattino con una probabilità di `probability`"""
    return PerturbationModule(
        perturbation_function=lambda tokens: [f"{tokens[0]}-{tokens[1]}"],
        token_grouping=2,
        probability=probability)


def addComma(token, punctChar):
    orginal_length = len(token)
    comma_pointer = 0
    if len(token) > 1:
        while comma_pointer < orginal_length:
            comma_pointer += randint(1, orginal_length - 1)
            if comma_pointer < orginal_length:
                token = token[:comma_pointer] + \
                    punctChar + token[comma_pointer:]
                comma_pointer += 1
    return token


def SplitWithCommaModule(probability: float,
                         punctChar: str) -> PerturbationModule:
    """ Funzione che genera moduli che dividono un token con delle virgole (o con qualsiasis stringa `punctChar`) con probabilità `probability` """
    return PerturbationModule(perturbation_function=lambda tokens:
                              [addComma(t, punctChar) for t in tokens],
                              token_grouping=1,
                              probability=probability)


def replaceChars(token: str, subData: dict) -> str:
    """ Funzione che perturba un token sostituiendo un uno o più caratteri con una stringa presa dall matrice di sostituzione """
    subProb = subData["count"]
    subMatrix = subData["subs"]
    appliable = {k: subProb[k] for k in subProb.keys() if k in token}
    subCandidates = list(appliable.keys())
    shuffle(subCandidates)
    tokenBitMask = [0 for char in token]
    for sub in subCandidates:
        subProb = appliable[sub]
        subWith = weighted_choice(subMatrix[sub])
        for start in find_all(token, sub):
            if sum(tokenBitMask[start:start + len(sub)]
                   ) == 0 and probability_boolean(subProb):
                token = token[:start] + subWith + token[start + len(sub):]
                tokenBitMask = tokenBitMask[:start] + \
                    [1 for c in subWith] + tokenBitMask[start+len(sub):]
    return token


def replaceChars_Tokens(tokens, subData):
    """ Funzione helper di charsubmodule """
    return [replaceChars(t, subData) for t in tokens]


def CharsSubModule(subMatrix: dict,
                   probability: int = 1) -> PerturbationModule:
    """ Funzione che genera moduli di sostituzione caratteri. Sono una necessarie la matrice di sostituizone e la probabilità """
    return PerturbationModule(perturbation_function=lambda tokens:
                              replaceChars_Tokens(tokens, subMatrix),
                              token_grouping=1,
                              probability=probability)


def generate_alternatives_for(token: str, subData: dict,
                              alternativesDict: dict, tokenAlternatives: int):
    """ Genera le n alternative per un certo token """
    altList = []
    i = 0
    while (len(altList) < tokenAlternatives and i < 50):
        i += 1
        t = replaceChars(token, subData)
        if t not in altList:
            altList.append(t)
    alternativesDict[token] = altList
    return altList


def replaceTokens(token: str, subData, alternativesDict: dict,
                  tokenAlternatives: int) -> str:
    """ Per ogni token, genero i 5 possibili misspellings se non già presenti nel dict
    In caso devo sostituire, vado a pescare nel dict """
    alternatives = alternativesDict.get(token, None)
    if not alternatives:
        alternatives = generate_alternatives_for(token, subData,
                                                 alternativesDict,
                                                 tokenAlternatives)
    alt_token = random_choice(alternatives)
    return alt_token


def replace_tokens(tokens, subData, alternativesDict, tokenAlternatives: int):
    """ Funzione helper di TokenSubModule """
    return [
        replaceTokens(t, subData, alternativesDict, tokenAlternatives)
        for t in tokens
    ]


def TokenSubModule(subMatrix,
                   tokenAlternatives=5,
                   alternativesDict={},
                   probability=1):
    """ Funzione che  crea moduli di sostituzione token. E' come il modulo di sostituzione caratteri, ma le parole sostituibili con un certo token sono predeterminate ad un numero di alternative `tokenAlternarives` """
    return PerturbationModule(
        perturbation_function=lambda tokens: replace_tokens(
            tokens, subMatrix, alternativesDict, tokenAlternatives),
        token_grouping=1,
        probability=probability)


class Pipeline:
    """ Classe che modella una pipeline di pertubazione """
    def __init__(self):
        self.modules = []

    def addModule(self, module: PerturbationModule):
        """ Aggiunge un modulo alla pipeline.
        
        Args:
            module(PertubationModule): modulo da aggiungere alla pipeline

        Returns:
            Ritorna la pipeline stessa, in modo da poter usare la concatenazione
         """
        self.modules.append(module)
        return self

    def run(self, input: list) -> list:
        """ Perturba una lista di token attraverso i moduli della pipeline 
        
        Args:
            input(`list(str)`): lista di token da perturbare
        """
        for module in self.modules:
            input = module.apply(input)
        return input

    def concatPipeline(self, other):
        """ Aggiunge alla pipeline tutti i modi dell'altra pipeline
        
        Args:
            other(`Pipeline`): pipeline da concatenare
         """
        self.modules = [*self.modules, *other.modules]
        return self

    def clone(self):
        """ Ritorna una copia della pipeline corrente """
        cloned = Pipeline()
        for module in self.modules:
            cloned.addModule(module)
        return cloned

    def addTokenization(self,
                        tkn_module: TokenizerModule,
                        dtkn_module: DetokenizerModule = None):
        """ Aggiunge alla pipeline corrente dei moduli di tokenizzazione e detokenizzazione all'inzio e alla fine 
        
        Args:
            tkn_module(`TokenizerModule`): modulo di tokenizzazione da aggiungere all'inizio
            dtkn_module('DetokenizerModule'): modulo di detokenizzazione da aggiungere alla fine
        """
        self.modules = [tkn_module, *self.modules]
        if (dtkn_module):
            self.modules = [*self.modules, dtkn_module]
        return self


class SuperPipeline:
    """Classe che permette di combinare una o più pipeline insieme
    """
    def __init__(self,
                 stickyness: int = 0,
                 block_size: int = 700,
                 detokenizer=DetokenizerModule) -> None:
        """ Costruttore base della classe

        Args:
            stickyness (:obj:`int`): Numero compreso fra 0 e 1. E' la probabilità che la pipeline di perturbazione rimanga la stessa dopo un blocco di codice

            block_size (:obj:`int`, optional): Lunghezza in caratteri di un blocco di testo, nel quale si unicamente una pipeline di pertubazione.

            detokinzer (:obj:`Detokenizer`): Eventuale modulo di detokenizzazione da aggiungere alla fine della superpipeline.
        """
        self.sub_pipelines = []
        self.sub_pipelines_weights = []
        self.block_size = block_size
        self.stickyness = stickyness
        self.detokenizer = detokenizer

    def addPipeline(self, pipeline: Pipeline, weight: int = 1) -> None:
        """ Funzione che aggiunge una pipeline di pertubazione alla superpipeline 
        
        Args:
            pipeline (:obj:`Pipeline`): pipeline da aggiungere

            weight (:obj:`int`, optional): peso della pipeline nell'insieme di tutte le pipeline. Maggiore è il peso, maggiore è la probabilità che la pipeline aggiunta sia usata per la perturbazione
        """
        self.sub_pipelines.append(pipeline)
        index = len(self.sub_pipelines) - 1
        self.sub_pipelines_weights.extend([index] * weight)

    def splitted(self, input: str) -> list:
        """ Funzione che ritorna la stringa `input` in blocchi di `self.block_size` caratteri 
        
        Args:
            input (:obj:`str`): stringa da dividere in blocchi
        """
        blocks = []
        bufferStr = ""
        for char in input:
            if len(bufferStr) < self.block_size or (
                    len(bufferStr) >= self.block_size and char != " "):
                bufferStr += char
            else:
                blocks.append(bufferStr)
                bufferStr = ""
        blocks.append(bufferStr)
        return blocks

    def run(self, input: str) -> str:
        """ Funzione che perturba in testo `input` con la Superpipeline definta 
        
        Args:
            input (:obj:`str`): stringa da perturbare
        """
        plain_blocks = self.splitted(input)
        perturbed_blocks = []
        current_pipeline = random_choice(self.sub_pipelines_weights)
        for pb in plain_blocks:
            if not probability_boolean(self.stickyness):
                current_pipeline = random_choice(self.sub_pipelines_weights)
            perturbed = self.sub_pipelines[current_pipeline].run(pb)
            perturbed_blocks.append(perturbed)
        perturbed_blocks = list(chain(*perturbed_blocks))
        return self.detokenizer.apply(perturbed_blocks)
