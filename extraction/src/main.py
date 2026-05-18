from pipeline.data_loader import *
from agents.agent import *
import json
import pandas as pd

if __name__ == '__main__':

    agent = Agent()

    list_csv, path_csv = find_csv_dataset()
    for i, csv_file in enumerate(list_csv):
        print(list_csv[i])
        # read titles and articles
        df_extract = load_data(path = f'{path_csv[i]}')

        # call llm
        client = agent.get_llm_client()

        dict_articles = {}
        errors = []
        for j, line in df_extract[((df_extract['label_logistic_reg']=='1') | (df_extract['label']==1)) & (~df_extract['title'].str.contains('Epstein')) & (~df_extract['title'].str.contains('Diddy'))].iterrows():
            try:
                title = line['text'].split("\nconteúdo: ")[0]
                text = line['text'].split("\nconteúdo: ")[1]
                answer_gemini = agent.call_llm(client = client, texto = text, temperature = 0.1)
                dict_ans = json.loads(answer_gemini.split("json\n")[1].replace("```", ""))
                dict_ans['portal'] = line['portal']
                dict_articles[title] = dict_ans
            except:
                errors.append(j)

        # save results
        save_data(pd.DataFrame(dict_articles), f'{list_csv[i].split(".csv")[0]}')

