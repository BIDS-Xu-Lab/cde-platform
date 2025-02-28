import os
import openai
import logging
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# LLM settings
# Set the API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

openai_chat_model = os.getenv("OPENAI_CHAT_MODEL")

logger.info('* loaded model %s' % os.getenv("EMBEDDING_MODEL"))
embedding_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL"))


def get_embedding_from_text(
    text_to_be_embedded,
    model = embedding_model
):
    '''
    Calculate the embedding of the title + abstracts
    '''
    # encode the texts
    logger.info("* encoding the texts ...")
    embeddings = model.encode(
        text_to_be_embedded,
        show_progress_bar=False,
    )
    return embeddings

