from fuzzywuzzy import process, fuzz

with open('toxic_vocab_extended_red.txt', 'r', encoding='utf-8-sig') as file:
    bad_words = file.read().split()



bad_words_optimized = ["УДАЛИТЬЬЬЬЬЬ"]

for index in range(len(bad_words)):
    print(f"Iteraction №{index} of {len(bad_words)}...")
    a = process.extractOne(bad_words[index], bad_words_optimized)
    if int(a[1]) < 60:
        bad_words_optimized.append(a[0])






for el in bad_words:
    if el != "удалить":
      bad_words_optimized.append(el)




with open('toxic_vocab_optimized.txt', 'w') as filehandle:
    for listitem in bad_words_optimized:
        filehandle.write('%s\n' % listitem)