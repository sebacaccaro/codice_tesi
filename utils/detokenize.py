from nltk.tokenize.treebank import TreebankWordDetokenizer


def detokenize(input):
    output = TreebankWordDetokenizer().detokenize(input)
    output = output.replace(" , ", ", ")
    output = output.replace(" ' ", "'")
    output = output.replace(" ’ ", "’")
    output = output.replace(" ’", "’")
    output = output.replace(" . ", ". ")
    output = output.replace(" : ", ": ")
    output = output.replace(" ; ", "; ")
    return output
