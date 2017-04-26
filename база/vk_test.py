from difflib import SequenceMatcher

def words_black(text):
    words =text.lower().split(' ')
    words_list=['блять']
    for i in words:
        for w in words_list:
            name = SequenceMatcher(lambda x: x in ' ',i , w).ratio()
            if name > 0.75:
                return name
    return name


print(words_black('блятм'))