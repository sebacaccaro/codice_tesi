import sys

sys.path.insert(0, "../utils/")
from utils import probability_boolean, find_all, randint, shuffle, random_choice, weighted_choice
from itertools import chain
from nltk import word_tokenize
from detokenize import detokenize


class SuperPipeline:
    def __init__(self, stickyness=0, block_size=700, detokenizer=None):
        self.sub_pipelines = []
        self.sub_pipelines_weights = []
        self.block_size = block_size
        self.stickyness = stickyness
        self.detokenizer = detokenizer

    def addPipeline(self, pipeline, weight=1):
        self.sub_pipelines.append(pipeline)
        index = len(self.sub_pipelines) - 1
        self.sub_pipelines_weights.extend([index] * weight)

    def splitted(self, input):
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

    def perturbedList(self, inputList):
        return [self.run(x) for x in inputList]

    # Input is just a long string

    def run(self, input):
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


class Pipeline:
    def __init__(self):
        self.modules = []

    def addModule(self, module):
        self.modules.append(module)
        return self

    def feedInput(self, tokens):
        self.input = tokens

    def run(self, input):
        for module in self.modules:
            input = module.apply(input)
        return input

    def concatPipeline(self, other):
        self.modules = [*self.modules, *other.modules]
        return self

    def clone(self):
        cloned = Pipeline()
        for module in self.modules:
            cloned.addModule(module)
        return cloned

    def addTokenization(self, tkn_module, dtkn_module=None):
        self.modules = [tkn_module, *self.modules]
        if (dtkn_module):
            self.modules = [*self.modules, dtkn_module]
        return self


class PerturbationModule:
    def __init__(self):
        self.function = None
        self.token_grouping = None
        self.probability = None

    def group(self, tokens):
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

    def __init__(self, perturbation_function, token_grouping, probability):
        self.perturbation_function = perturbation_function
        self.token_grouping = token_grouping
        self.probability = probability

    def apply(self, tokens):
        perturbed_list = [
            self.perturbation_function(t)
            if probability_boolean(self.probability)
            and len(t) == self.token_grouping else t
            for t in self.group(tokens)
        ]
        return list(chain.from_iterable(perturbed_list))


class TokenizerModule:
    def apply(self, input):
        return word_tokenize(input)


class DetokenizerModule:
    def apply(self, input):
        return detokenize(input)


def split(token):
    return " ".join([char for char in token])


def split_tokens(list_of_tokens):
    return [split(t) for t in list_of_tokens]


def SplitModuleGenerator(probability):
    return PerturbationModule(perturbation_function=split_tokens,
                              token_grouping=1,
                              probability=probability)


def AddPunctuationModule(probability, punctChar):
    return PerturbationModule(
        perturbation_function=lambda tokens: [*tokens, punctChar],
        token_grouping=1,
        probability=probability)


def MergeWordHyphenModule(probability):
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


def SplitWithCommaModule(probability, punctChar):
    return PerturbationModule(perturbation_function=lambda tokens:
                              [addComma(t, punctChar) for t in tokens],
                              token_grouping=1,
                              probability=probability)


def replaceChars(token, subData):
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
    return [replaceChars(t, subData) for t in tokens]


def CharsSubModule(subMatrix, probability=1):
    return PerturbationModule(perturbation_function=lambda tokens:
                              replaceChars_Tokens(tokens, subMatrix),
                              token_grouping=1,
                              probability=probability)


def generate_alternatives_for(token: str, subData: dict,
                              alternativesDict: dict, tokenAlternatives: int):
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
                  tokenAlternatives: int):
    # Per ogni token, genero i 5 possibili misspellings se non già presenti nel dict
    # In caso devo sostituire, vado a pescare nel dict
    alternatives = alternativesDict.get(token, None)
    if not alternatives:
        alternatives = generate_alternatives_for(token, subData,
                                                 alternativesDict,
                                                 tokenAlternatives)
    alt_token = random_choice(alternatives)
    return alt_token


def replace_tokens(tokens, subData, alternativesDict, tokenAlternatives: int):
    return [
        replaceTokens(t, subData, alternativesDict, tokenAlternatives)
        for t in tokens
    ]


def TokenSubModule(subMatrix,
                   tokenAlternatives=5,
                   alternativesDict={},
                   probability=1):
    return PerturbationModule(
        perturbation_function=lambda tokens: replace_tokens(
            tokens, subMatrix, alternativesDict, tokenAlternatives),
        token_grouping=1,
        probability=probability)
