from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, average_precision_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def evaluate_model(y_test, y_pred, type_model, name_model):
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    prec_auc = average_precision_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print(f'O modelo de {type_model} {name_model} teve as seguintes métricas:\nAcurácia: {acc}\nF1: {f1}\nPrecisão: {prec}\nRecall: {recall}\nPR-AUC: {prec_auc}')

    return {
            'acc': acc,
            'f1': f1,
            'precision': prec,
            'recall': recall,
            'prec_auc': float(prec_auc),
            'conf_matrix': conf_matrix.tolist()
        }

def generate_charts(df, prob_column, metrics, name_model, embedding_model):
    project_path = Path().resolve()
    path = fr'{project_path}\src\data\train\metrics\{embedding_model}'

    sns.histplot(data=df, x=prob_column, bins=50, kde=True)
    plt.xlabel('Probabilidade de Y')
    plt.ylabel('Densidade')
    plt.xlim((0,1))
    plt.title('Histograma das Probabilidades de Y')
    plt.tight_layout()
    plt.savefig(fr'{path}\hist_prob_{name_model}.png', dpi=300)
    plt.clf()

    display_labels = ["Não Tráfico Humano", "Tráfico Humano"]
    disp = ConfusionMatrixDisplay(confusion_matrix=np.array(metrics['conf_matrix']), display_labels=display_labels)

    disp.plot(cmap='Reds')

    plt.title("Matriz de Confusão")
    plt.xlabel("Rótulos Preditos")
    plt.ylabel("Rótulos Verdadeiros")
    plt.tight_layout()
    plt.savefig(fr'{path}\confusion_matrix_{name_model}.png', dpi=300)
    plt.clf()

def generate_fn_over_positives(df, name, embedding_model, models):
    project_path = Path().resolve()
    path = fr'{project_path}\src\data\train\metrics\{embedding_model}'

    y_vdd = df['label']
    thresholds = np.linspace(0, 1, 100)
    fn_sobre_pos_list = []

    #for model in ['XGBoost', 'SVM', 'logistic_regression', 'naive_bayes']:
    for model in models:
        y_prob = df[f'prob_label_{model}_{embedding_model}']
        for t in thresholds:
            y_pred = (y_prob >= t).astype(int)

            vn, fp, fn, vp = confusion_matrix(y_vdd, y_pred).ravel()

            if (fn + vp) > 0:
                fn_sobre_pos = fn / (fn + vp)
            else:
                fn_sobre_pos = 0

            fn_sobre_pos_list.append((model, t, fn_sobre_pos))

    df_fn_sobre_pos = pd.DataFrame(fn_sobre_pos_list, columns=['model', 'threshold', 'fn_pos'])

    palette = {
        'XGBoost': '#880808',
        'SVM': '#F88379',
        'logistic_regression': '#FF4433',
        'naive_bayes': '#FF6F61'
    }

    sns.lineplot(data=df_fn_sobre_pos, x='threshold', y='fn_pos', hue='model', palette=palette, linewidth=2.5)
    plt.title("Proportion of False Negatives Among Positives Cases versus Threshold")
    plt.xlabel("Threshold")
    plt.ylabel("Proportion")
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(fr'{path}\fn_sobre_pos_{name}.png', dpi=300)
    plt.clf()

def pdf_header_metrics(pdf, name, embedding_model, baseline, shape):
    pdf.set_text_color(120, 0, 0)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Relatório de Métricas dos Modelos de Classificação", align="C", ln=True)
    pdf.set_draw_color(120, 0, 0)
    pdf.set_line_width(0.8)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica","B", 12)
    pdf.cell(0, 10, f"Dataset utilizado: {name}", ln=True)
    pdf.cell(0, 10, f"Modelo utilizado para o embedding dos textos: {embedding_model}", ln=True)
    pdf.cell(0, 10, f"Número de linhas presentes: {shape}", ln=True)
    pdf.cell(0, 10, f"Proporção dos casos positivos: {baseline}", ln=True)
    data_hoje = datetime.today().strftime("%d/%m/%Y")
    pdf.cell(0, 8, f"Data de geração: {data_hoje}", ln=True)
    pdf.ln(10)

    return pdf

def save_metrics(pdf, metrics, name_model, type_model, embedding_model):

    # Título
    pdf.set_text_color(120, 0, 0)
    pdf.set_font("Helvetica", "B", size= 12)
    pdf.cell(0, 10, f"Métricas - Modelo {name_model}", ln=True)
    pdf.cell(0, 10, f"Modelo de Classificação: {type_model}", ln=True)
    pdf.ln(5)

    # Métricas
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Acurácia: {metrics['acc']:.2f}", ln=True)
    pdf.cell(0, 8, f"Dos classificados como positivo, quantos realmente são? Precisao (VP/(VP + FP)): {metrics['precision']:.2f}", ln=True)
    pdf.cell(0, 8, f"De todos os casos positivos reais, quantos o modelo conseguiu detectar? Recall (VP/(VP + FN)): {metrics['recall']:.2f}", ln=True)
    pdf.cell(0, 8, f"Média harmônica entre Precisão e Recall. F1 - Score: {metrics['f1']:.2f}", ln=True)
    pdf.cell(0, 8, f"PR AUC (Precisão x Recall). Baseline é a proporção de positivos.: {metrics['prec_auc']:.2f}", ln=True)

    project_path = Path().resolve()
    path = fr'{project_path}\src\data\train\metrics\{embedding_model}'

    # Inserir imagem da matriz
    pdf.set_text_color(133, 0, 0)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0,8, "Matriz de Confusão", ln=True)
    pdf.image(fr'{path}\confusion_matrix_{name_model}.png', x=50, w=100)

    pdf.ln(10)

    return pdf

def save_charts_and_pdf(pdf, models, name_model, embedding_models):
    pdf.set_text_color(133, 0, 0)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Comparação de Métricas dos Modelos", ln=True)
    pdf.set_draw_color(120, 0, 0)
    pdf.set_line_width(0.8)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)
    pdf.ln(5)

    project_path = Path().resolve()
    path_save_pdf = fr'{project_path}\src\data\train\metrics'

    for embedding_model in embedding_models:
        path = fr'{project_path}\src\data\train\metrics\{embedding_model}'

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(0, 8, f"Falsos Negativos sobre Positivos dos Modelos - {name_model}", align="C", ln=True)
        pdf.image(fr'{path}\fn_sobre_pos_{name_model}.png', x=50, w=100)

        dict_chart = {
            'confusion_matrix': 'Matriz de Confusão',
            'hist_prob': 'Histograma das Probabilidades'
        }

        for chart, name_chart in dict_chart.items():
            for model in models:
                # Inserir imagem da matriz e dos histogramas
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "B", size=12)
                pdf.cell(0, 8, f"{name_chart} - Modelo {model} e Dataset {name_model}", align="C", ln=True)
                pdf.image(fr'{path}\{chart}_{name_model}_{model}.png', x=50, w=100)

    pdf.output(fr'{path_save_pdf}\{name_model}_metrics.pdf')
