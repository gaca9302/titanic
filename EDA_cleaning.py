import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os, re, string
    import pandas as pd
    import numpy as np
    from pymystem3 import Mystem
    from tqdm import tqdm

    tqdm.pandas()

    current_dir = os.getcwd()
    print(f"Текущая директория: {current_dir}")
    return Mystem, np, pd, re


@app.cell
def _():
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords')
    return (stopwords,)


@app.cell
def _(pd):
    train_df = pd.read_csv("../data/raw/train.csv")
    eval_df = pd.read_csv("../data/raw/eval.csv")
    print(train_df.shape)
    print(eval_df.shape)

    duplicated_rows = train_df[train_df.duplicated(subset=['description', 'price'])].shape[0]
    print("duplicated_rows:", duplicated_rows)

    # Delete duplicates
    train_df = train_df.drop_duplicates(subset=['description', 'price'], keep=False)
    print(train_df.shape)

    duplicated_rows = train_df[train_df.duplicated(subset=['description', 'price'])].shape[0]
    print("duplicated_rows after:", duplicated_rows)
    return (train_df,)


@app.cell
def _(pd):
    pd.read_csv("../data/raw/train.csv").loc[9851]
    return


@app.cell
def _(train_df):
    train_df.sample(10)
    return


@app.cell
def _(np, pd, re, train_df):
    def process_ceiling_height(info):
        height_match = re.search(r'потолки (\d+(\.\d+)?)м', info)
        if height_match:
            height = float(height_match.group(1))
            if 2 <= height <= 8:
                return height
        return None

    heights = train_df.description.apply(lambda x: process_ceiling_height(x)) 


    train_df.insert(0, 'area', train_df.title.str.extract(r'(\d+(\.\d+)?) м²')[0].astype(float))
    train_df.insert(1, 'room', train_df.title.str.extract(r'(\d+)-комнатная')[0].astype(int))
    train_df.insert(2, 'floor', pd.to_numeric(train_df.title.str.extract(r'(\d{1,2})/(\d{1,2}) этаж')[0], errors='coerce'))
    train_df.insert(3, 'floor_count', pd.to_numeric(train_df.title.str.extract(r'(\d{1,2})/(\d{1,2}) этаж')[1], errors='coerce'))
    train_df.insert(4, 'ceiling_height', heights)
    train_df.insert(5, 'year', train_df.description.str.extract(r'(\d{4}) г\.п|(\d{4}) г\.п\.')[0].astype(int)) 
    train_df.insert(6, 'house_type', train_df.description.str.extract(r'(\w+ дом)')[0]) 

    train_df.house_type = train_df.house_type.apply(lambda x: x if x in ['монолитный дом', 'кирпичный дом', 'панельный дом'] else np.nan)
    train_df.address = train_df.address.apply(lambda x: x.split(' — ')[0] if ' — ' in x else x)

    train_df.description = train_df.description.str.replace(r'(\w+ дом)', '', regex=True)
    train_df.description = train_df.description.str.replace(r'(\d{4}) г\.п|(\d{4}) г\.п\.', '', regex=True)
    train_df.description = train_df.description.str.replace(r'потолки (\d+(\.\d+)?)м', '', regex=True)

    train_df.drop(columns=['id', 'url', 'title', 'date'], inplace=True)
 
    return


@app.cell
def _(train_df):
    train_df.insert(6, 'ceiling_height2', train_df['ceiling_height'])
    return


@app.cell
def _(Mystem, np, re, ru_stopwords):
    def remove_emoji(string):
        """
        Удаление эмоджи из текста
        """
        emoji_pattern = re.compile("["u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u'\U00010000-\U0010ffff'
                                   u"\u200d"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\u3030"
                                   u"\ufe0f"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)


    def remove_links(string):
        """
        Удаление ссылок
        """
        string = re.sub(r'http\S+', '', string)  # remove http links
        string = re.sub(r'bit.ly/\S+', '', string)  # rempve bitly links
        string = re.sub(r'www\S+', '', string)  # rempve bitly links
        string = string.strip('[link]')  # remove [links]
        return string


    def preprocessing(string, stopwords, stem):
        """
        Простой препроцессинг текста, очистка, лематизация, удаление коротких слов
        """
        string = remove_emoji(string)
        string = remove_links(string)
        string = string.lower()

        # удаление символов "\r\n"
        str_pattern = re.compile("\r\n")
        string = str_pattern.sub(r'', string)

        # очистка текста от символов
        string = re.sub('(((?![a-zа-яёәғқңөұүһі ]).)+)', ' ', string)
        # лематизация
        # string = ' '.join([
        #     re.sub('\\n', '', ' '.join(stem.lemmatize(s))).strip()
        #     for s in string.split()
        # ])
        # удаляем слова короче 3 символов
        # string = ' '.join([s for s in string.split() if len(s) > 3])
        # удаляем стоп-слова
        string = ' '.join([s for s in string.split() if s not in stopwords])
        return string


    def get_clean_text(data, stopwords):
        """
        Получение текста в преобразованной после очистки
        матричном виде, а также модель векторизации
        """
        # Простой препроцессинг текста
        stem = Mystem()
        comments = [preprocessing(x, stopwords, stem) for x in data]
        # Удаление комментов, которые имеют меньше, чем 5 слов
        comments = [y for y in comments if len(y.split()) > 5]
        # common_texts = [i.split(' ') for i in comments]
        return comments


    def vectorize_text(data, tfidf):
        """
        Получение матрицы кол-ва слов в комменариях
        Очистка от пустых строк
        """
        # Векторизация
        X_matrix = tfidf.transform(data).toarray()
        # Удаляем строки в матрице с пустыми значениями
        mask = (np.nan_to_num(X_matrix) != 0).any(axis=1)
        return X_matrix[mask]

    def func(x):
        stem = Mystem()
        return preprocessing(x, ru_stopwords, stem)

    return (func,)


@app.cell
def _(stopwords):
    ru_stopwords = set(stopwords.words('russian'))
    ru_stopwords.update(['этаж', 'г.п', 'р-не'])
    return (ru_stopwords,)


@app.cell
def _(pd):
    train_df = pd.read_csv("../data/raw/train.csv")
    eval_df = pd.read_csv("../data/raw/eval.csv")
    return (train_df,)


@app.cell
def _(train_df):
    df = train_df.copy()
    return (df,)


@app.cell
def _(df, re):
    df['a'] = df.description.progress_apply(lambda x: re.sub('(((?![әғқңөұүһі ]).)+)', ' ', x))
    return


@app.cell
def _(df, pd):
    df["a"] = df["a"].astype(str).str.strip().replace("", pd.NA)
    return


@app.cell
def _(func, train_df):
    train_df.description = train_df.description.progress_apply(func)
    return


@app.cell
def _():
    # from deep_translator import GoogleTranslator
    # 1. Инициализируем переводчик
    # translator = GoogleTranslator(source='kk', target='ru')
    # # 2. Функция для перевода одной строки
    # def translate_text(text):
    #     if pd.isna(text) or text.strip() == "":
    #         return text
    #     try:
    #         return translator.translate(text)
    #     except Exception as e:
    #         return f"Error: {e}"
    # # 3. Применяем с прогресс-баром
    # tqdm.pandas(desc="Перевод")
    # bb['text_ru'] = bb['description'].progress_apply(translate_text)
    return


@app.cell
def _(bb):
    bb  
    return


@app.cell
def _(df):
    bb = df[~df.a.isna()].copy()
    return (bb,)


@app.cell
def _(train_df):
    train_df[:3]
    return


@app.cell
def _():
    # m = Mystem()
    # all_texts = " | ".join(train_df['description'].astype(str))
    # # Лемматизируем всё за один запуск процесса
    # lemmas_all = m.lemmatize(all_texts)
    # # Собираем обратно и разбиваем по нашему маркеру
    # full_result = "".join(lemmas_all)
    # train_df['description'] = full_result.split(" | ")
    return


@app.cell
def _(train_df):
    train_df[:3]
    return


@app.cell
def _():
    from langdetect import detect

    return (detect,)


@app.cell
def _(detect, train_df):
    def process_mixed_text(text):
        try:
            lang = detect(text)
        except:
            lang = 'unknown'

        if lang == 'ru':

            return "ru"
        elif lang == "kk":
            return "kk"
    train_df['text_l'] = train_df['description'].progress_apply(process_mixed_text)
    return


@app.cell
def _(train_df):
    train_df[train_df.text_l == "kk"].shape
    return


@app.cell
def _(train_df):
    train_df[train_df.text_l == "kk"]
    return


@app.cell
def _():
    from deep_translator import GoogleTranslator
    tr = GoogleTranslator(source='kk', target='ru')
    return (tr,)


@app.cell
def _(bb, full_result, tr):

    # 2. Функция для перевода одной строки
    all_ = " || ".join(bb['description'].astype(str))
    # Лемматизируем всё за один запуск процесса
    leml = tr.translate(all_)
    # Собираем обратно и разбиваем по нашему маркеру
    full_r = "".join(leml)
    bb['de'] = full_result.split(" || ")
    return (all_,)


@app.cell
def _(all_):
    all_
    return


@app.cell
def _(train_df):
    train_df.ceiling_height.value_counts(dropna=False)
    return


@app.cell
def _(train_df):
    train_df.floor_count.value_counts(dropna=False)
    return


@app.cell
def _(re, train_df):
    train_df['height_match'] = train_df.description.apply(lambda x: re.search(r'потолки (\d+(\.\d+)?)м', x))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
