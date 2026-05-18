from sentence_transformers import SentenceTransformer

def call_embedding_model(model):
    # pre-trained model for text embedding
    model = SentenceTransformer(model)
    return model

def text_embedding(column_df, model):
    return model.encode(column_df, show_progress_bar=True)

