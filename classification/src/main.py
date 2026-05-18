from pipeline.data_loader import *
from models.training.models import *
from models.training.train_model import *
from models.training.metrics import *
from models.training.text_embedding import *
import argparse
import numpy as np
from fpdf import FPDF
import json
from sklearn.feature_extraction.text import CountVectorizer

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--embedding-models', nargs='+', type=str, required=True)
    parser.add_argument('--train', action='store_true')
    parser.add_argument('--test-size', type=float)
    parser.add_argument('--name-model', type=str)
    parser.add_argument('--models', type=str, nargs='+', choices=["Logistic Regression", "Random Forest",'SVM', 'XGBoost',"Naive Bayes"], required=True)

    args = parser.parse_args()
    print(args.train)
    if args.train and args.test_size is None and args.name_model is None:
        parser.error('--test-size e --name-model obrigatórios quando --train é passado')
    elif args.train and args.test_size is None:
        parser.error('--test-size obrigatório quando --train é passado')
    elif args.train and args.name_model is None:
        parser.error('--name-model obrigatório quando --train é passado')

    print(args)

    if args.train == True:
        print('Treinando modelo com dados')
    else:
        print('Classificando dados')

    print(f'Modelos escolhidos: {args.models}')

    # find csv and load data
    csv_files, path_csv_files = find_csv_dataset(train=args.train)
    print(f'Arquivos achados: {csv_files}')

    # call models
    models_type = args.models
    models_type_name = {
        "Logistic Regression":'logistic_regression',
        'SVM':'SVM',
        'XGBoost':'XGBoost',
        "Random Forest":'random_forest',
        "Naive Bayes":'naive_bayes'
    }
    models = {models_type_name[type]: call_model(type) for type in models_type}

    # classify titles for each csv file in data-in directory
    for csv_file in path_csv_files:
        dict_metrics = {}

        csv_name = Path(csv_file).name.split('.')[0]

        df_titles = load_data(csv_file)
        print(df_titles.head())
        y = df_titles['label'].to_numpy()

        for embedding_model in args.embedding_models:

            # calling the embedding model
            embedding_model_instance = call_embedding_model(embedding_model)

            # creating path for each model used for text embedding
            project_path = Path().resolve()

            # for metrics directory
            path = fr'{project_path}\src\data\train\metrics\{embedding_model}'
            check_or_create_directory(path)

            # for dataset out directory
            path = fr'{project_path}\src\data\train\out\{embedding_model}'
            check_or_create_directory(path)

            # text embedding
            print('-----------------------------------------\n\n')
            print(f'fazendo embedding do modelo: {embedding_model}')
            print('-----------------------------------------\n\n')
            df_titles['embedding'] = df_titles['text'].apply(lambda x: text_embedding(x, embedding_model_instance))

            # if the code will train some model
            if args.train == True:
                base_line = df_titles[df_titles['label'] == 1].shape[0]/df_titles.shape[0]

                # split data in train dataset and test dataset
                # X = embedding and y = label
                X_train, X_test, y_train, y_test = train_test_split(df_titles,
                                                                    y,
                                                                    test_size=args.test_size,
                                                                    random_state=1234,
                                                                    stratify=y
                                                                    )

                df_x_train = X_train
                df_x_test = X_test

                X_train = np.vstack(X_train['embedding'].values)
                X_test = np.vstack(X_test['embedding'].values)

                # funcao standardize_x
                X_train, X_test = standardize_x(X_train, X_test)

                for type_model, model in models.items():

                    if type_model == 'naive_bayes':
                        _, counts = np.unique(y, return_counts=True)
                        freq = counts / counts.sum()
                        print("\nFREQUENCIA DAS CLASSES::::::\n")
                        print(freq)
                        model = call_model("Naive Bayes", class_weight_NB= freq)

                        # vectorizer
                        vectorizer = CountVectorizer()
                        texts_train = [clean_text_for_naive_bayes(x) for x in df_x_train['text']]
                        X_train = vectorizer.fit_transform(texts_train)

                        texts_test = [clean_text_for_naive_bayes(x) for x in df_x_test['text']]
                        X_test = vectorizer.transform(texts_test)


                    # train model
                    train_model(model, X_train, y_train, name_model=f'{csv_name}_{type_model}', embedding_model= embedding_model)

                    # predict values
                    y_pred, y_prob = predict_model(model, X_test)
                    df_x_test[f'pred_label_{type_model}_{embedding_model}'] = y_pred
                    df_x_test[f'prob_label_{type_model}_{embedding_model}'] = y_prob
                    df_x_test[f'embedding_{embedding_model}'] = df_x_test['embedding']

                    # including column with label given by the model in df_titles
                    df_titles = df_titles.merge(df_x_test[['text',f'pred_label_{type_model}_{embedding_model}',f'prob_label_{type_model}_{embedding_model}']], on='text', how='left')

                    # metrics
                    metrics = evaluate_model(y_test, y_pred, type_model, name_model=f'{csv_name}_{type_model}')
                    print(metrics)

                    # saving metrics by model
                    dict_metrics[f'{csv_name}_{type_model}_{embedding_model}'] = metrics

                    # generate chart metrics
                    generate_charts(df = df_x_test, prob_column= f'prob_label_{type_model}_{embedding_model}', metrics = metrics, name_model=f'{csv_name}_{type_model}', embedding_model=embedding_model)

                # saving test dataset with embedding and predicted labels
                save_df(df=df_x_test, df_name=f'{csv_name}_complete_{embedding_model}', train=True)

                # generating chart with proportion of false negatives over positives versus thresholds
                generate_fn_over_positives(df = df_x_test, name=f'{csv_name}', embedding_model=embedding_model, models = list(models.keys()))

            # if the code will classify titles
            else:
                df_x = df_titles
                X = np.vstack(df_x['embedding'].values)

                for type_model, model in models.items():

                    y_pred, y_prob = predict_model(model, X)
                    df_x['pred_label'] = y_pred
                    df_x['prob_label'] = y_prob

                    save_df(df=df_x, name_model=f'{csv_name}_{type_model}', embedding_model= embedding_model, train=False, models = list(models.keys()))

        with open(fr'{project_path}\src\data\train\teste.json', 'w', encoding='utf-8') as f:
            json.dump(dict_metrics, f, indent=4)

        cols_delete = [col for col in df_titles.columns if 'embedding' in col]
        df_titles.drop(cols_delete, axis = 1, inplace = True)
        # saving original dataset with predicted labels and without embedding of the texts
        save_df(df=df_titles, df_name=f'{csv_name}_without_embedding', train=True)
        # saving test dataset with predicted labels and without embedding of the texts
        save_df(df=df_titles[~df_titles[f'prob_label_{type_model}_{embedding_model}'].isna()], df_name=f'{csv_name}_test_without_embedding', train=True)

        # generate pdf with metrics or divergences
        pdf = FPDF()
        pdf.add_page()

        #pdf = pdf_header_metrics(pdf, name = csv_name, embedding_model = args.embedding_model, baseline = base_line, shape= df_titles.shape[0])

        print(dict_metrics)

        for embedding_model in args.embedding_models:
            print(f'Incluindo pagina do modelo {embedding_model} para o csv {csv_name}')
            pdf.add_page()
            pdf = pdf_header_metrics(pdf, name=csv_name, embedding_model=embedding_model, baseline=base_line,
                                     shape=df_titles.shape[0])
            for type in models_type:
                print(f'Nome do modelo: {csv_name}_{models_type_name[type]}')
                if args.train == True:
                    pdf = save_metrics(pdf = pdf, metrics = dict_metrics[f'{csv_name}_{models_type_name[type]}_{embedding_model}'], name_model = f'{csv_name}_{models_type_name[type]}', type_model = type, embedding_model=embedding_model)
            # for model, metrics in dict_metrics.items():
            #     if args.train == True:
            #         pdf = save_metrics(pdf = pdf, metrics = metrics, name_model = )

            pdf.add_page()

        pdf = save_charts_and_pdf(pdf = pdf, models = models.keys(), name_model= csv_name, embedding_models=args.embedding_models)

