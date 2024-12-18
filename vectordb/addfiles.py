from langchain_huggingface import HuggingFaceEmbeddings

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