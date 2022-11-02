from nltk.corpus import wordnet as wn
from nltk import download
import logging
import ssl

logger = logging.getLogger("wordnet")
logger.setLevel(logging.DEBUG)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

download('wordnet')
download('omw-1.4')
labels_from_model = [
    'Bicycle',
    'Bridges',
    'Bus',
    'Car',
    'Chimney',
    'Crosswalk',
    'Fire_Hydrant',
    'Motorcycle',
    'Palm_Tree',
    'Traffic_Light',
    'Boat'
    ]

thresholds_for_label = {
    'Bicycle': 26.,
    'Bridges': 23.,
    'Bus': 24.5,
    'Car': 43.5,
    'Chimney' : 33.5,
    'Crosswalk': 18.,
    'Fire_Hydrant': 11.,
    'Motorcycle': 41.,
    'Palm_Tree': 37.,
    'Traffic_Light':36.,
    'Boat':18.
}

def get_most_similar_label(words):
    logger.debug("Processing: %s",words)
    label_synsets = []
    logger.debug("Models labels: %s", labels_from_model)
    for label in labels_from_model:
        label_synsets.append(wn.synsets(label)[0])
    result = []
    indices = []
    for word in words:
        if word.startswith("a "):
            word = word[2:]
        word_with_tabs = word.replace(' ', '_')
        word_synset = wn.synsets(word_with_tabs)[0]
        max_similarity = 0
        result_index = -1
        index = 0
        for label_synset in label_synsets:
            similarity = label_synset.wup_similarity(word_synset)
            logger.info("%s is %1.3f similar with %s", word, similarity,labels_from_model[index])
            if similarity > max_similarity:
                max_similarity = similarity
                result_index = index
            index += 1
        if max_similarity > 0.8:
            result.append(labels_from_model[result_index])
            indices.append(result_index)
        else:
            logger.warn("Max similarity of %s with available labels too small: %s",word, str(max_similarity))
        logger.debug("Result is : %s", result)
    return result, indices