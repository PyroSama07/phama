from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from uuid import uuid4
import os
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL=os.getenv('QDRANT_URL')

def get_doc(path):
    f = open(path,encoding="utf8")
    sample_doc = f.read()
    f.close()
    sample_doc = sample_doc.replace('\n\n','#sentencesahikarnekeliyerandomvariable')
    sample_doc = sample_doc.replace('\n' ,'')
    sample_doc = sample_doc.replace('#sentencesahikarnekeliyerandomvariable','\n\n')
    return sample_doc

model_name = 'l3cube-pune/punjabi-sentence-similarity-sbert'
embeddings = HuggingFaceEmbeddings(
    model_name=model_name)

veg_doc = get_doc('pp_veg_pbi.txt')
kharif_doc = get_doc('pp_kharif_pbi.txt')
rabi_doc = get_doc('pp_rabi_pbi.txt')
fruits_doc = get_doc('pp_fruits_pbi.txt')
citrus_doc = get_doc('Citrus_Cultivation_pbi.txt')

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200,chunk_overlap=100)
splits = text_splitter.create_documents(texts = [veg_doc,kharif_doc,rabi_doc,fruits_doc,citrus_doc])

client = QdrantClient(QDRANT_URL,timeout=60)
COLLECTION_NAME="phama"

if not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embeddings.client.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

    uuids = [str(uuid4()) for _ in splits]  # Create a unique ID for each document
    # print(uuids[9])

    vector_store.add_documents(documents=splits, ids=uuids)