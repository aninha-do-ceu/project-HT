import pickle
from pathlib import Path
import re

from models.training.models import check_model_type
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def standardize_x(X_train, X_test):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test

def train_model(model, X_train, y_train, name_model, embedding_model):
    model.fit(X_train, y_train)

    project_path = Path().resolve()
    model_type = check_model_type(model)

    path = fr'{project_path}\src\models\trained\{model_type}\{name_model}_{embedding_model}.pkl'
    print(f'Salvando modelo em {path}')

    with open(path, 'wb') as file:
        pickle.dump(model, file)

    return model


def predict_model(model, X_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]
    return y_pred, y_prob

def clean_text_for_naive_bayes(text):
    texto = text.lower()
    pontos = r"[.,:+\"']"
    texto_limpo = re.sub(pontos, '', texto)

    palav = ['a', 'o', 'título', 'conteúdo', 'e', 'à', 'ao', 'epstein', 'diddy', 'os', 'são', 'em', 'ele', 'ela']
    # pattern_palav = r'\b(?:' + '|'.join(map(re.escape, palav)) + r')\b'
    pattern_palav = r'(?<!-)\b(?:' + '|'.join(map(re.escape, palav)) + r')\b(?!-)'

    texto_limpo = re.sub(pattern_palav, '', texto_limpo)
    texto_limpo = texto_limpo.strip()

    return texto_limpo