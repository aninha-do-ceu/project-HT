"""
Base para a chamada dos modelos
Métodos:
    call_model
    check_model_type
"""
from typing import Optional, Sequence

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB

def check_model_type(model):
    if isinstance(model, LogisticRegression):
        # print(f"The parameter is a LogisticRegression instance: {model}")
        return 'logistic_regression'
    elif isinstance(model, SVC):
        # print(f"The parameter is a SVM instance: {model}")
        return 'SVM'
    elif isinstance(model, xgb.XGBClassifier):
        # print(f"The parameter is a XGBoost instance: {model}")
        return 'XGBoost'
    elif isinstance(model, RandomForestClassifier):
        return 'random_forest'
    elif isinstance(model, MultinomialNB):
        return 'multinomial_nb'
    else:
        raise ValueError(f"The parameter is none of Logistic Regression, SVM, XGBoost, Random Forest or Naive Bayes. It is of type: {type(model)}")

def call_model(model_type, random_state: Optional[int] = 1234, class_weight_NB: Optional[Sequence[float]] = None):
    if model_type == "Logistic Regression":
        return LogisticRegression(
            class_weight = 'balanced',
            random_state = random_state,
            max_iter=2000
        )
    elif model_type == "SVM":
        return SVC(
            class_weight='balanced',
            probability = True,
            random_state=random_state
        )
    elif model_type == "XGBoost":
        return xgb.XGBClassifier()
    elif model_type == "Random Forest":
        return RandomForestClassifier(
            class_weight = 'balanced',
            n_estimators=30,
            random_state=random_state
        )
    elif model_type == "Naive Bayes":
        if class_weight_NB is not None:
            return MultinomialNB(
                class_prior=class_weight_NB
            )
        else:
            return MultinomialNB()
    else:
        raise ValueError("The parameter is none of Logistic Regression, Random Forest, SVM, Naive Bayes or XGBoost. Select: Logistic Regression, Random Forest, SVM, XGBoost.\n")

