from pathlib import Path
from tokenize import String
import spacy
import random
from pattern.en import comparative, superlative, pluralize
import mlconjug3

nlp = spacy.load("en_core_web_sm")
conjugator = mlconjug3.Conjugator(language="en")

with Path("words.txt").open("r") as f:
    FILE_CONTENTS = f.read().splitlines()
    words = {}
    nouns = []
    verbs = []
    for line in FILE_CONTENTS:
        word = line.split(": ")[0]
        if word.endswith("]"):
            if word.endswith("[NOUN]"):
                word = word.split("[")[0]
                nouns.append(word)
            if word.endswith("[VERB]"):
                word = word.split("[")[0]
                verbs.append(word)

        words[word] = line.split(": ")[1].split(", ")

MORPHOLOGY = {
    "Degree": {"Cmp": comparative, "Sup": superlative},
    "Number": {"Plur": pluralize},
}

VERB_MORPH_NAMES = {"Sing": "s", "Plur": "p", "Pres": "present", "Past": "past tense"}


def _conjugator(token, word: String):
    tense = VERB_MORPH_NAMES[token.morph.get("Tense")[0]]
    person = token.morph.get("Person")[0]
    number = VERB_MORPH_NAMES[token.morph.get("Number")[0]]
    return conjugator.conjugate(word).conjug_info["indicative"][f"indicative {tense}"][
        person + number
    ]


def _morph_replace(text: String, token, word2: String):
    morph = token.morph

    if token.pos_ != "VERB":
        # Convert the noun or adjective to a form that matches it's morphology
        for morph_type in MORPHOLOGY:
            try:
                word2 = MORPHOLOGY[morph_type][morph.get(morph_type)[0]](word2)
            except IndexError:
                pass
    else:
        word2 = _conjugator(token, word2)

    return text.replace(token.text, word2)


def smartify(text: String):
    """Returns a pretentious version of the inputted text."""
    doc = nlp(text)
    new_text = text

    for token in doc:
        if token.lemma_ in words:
            is_wrong_form_verb = token.lemma_ in verbs and token.pos_ != "VERB"
            is_wrong_form_noun = token.lemma_ in nouns and token.pos_ != "NOUN"
            if is_wrong_form_verb or is_wrong_form_noun:
                continue
            print(token.text)
            new_text = _morph_replace(
                new_text, token, random.choice(words[token.lemma_])
            )

    return new_text


print(smartify("I'm feeling really hungry right now, I think I'll eat some carrots."))
