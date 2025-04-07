import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import faiss

# Load env vars
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="SHL Assessment Recommender", page_icon="🧠")
st.title("🔍 SHL Assessment Recommender")

@st.cache_resource
def load_model_and_data():
    df = pd.read_csv("Data.csv")
    df["combined"] = df.apply(lambda row: f"""Title: {row['title']}
Description: {row['description']}
Assessment Length: {row['Assesment Length']}
Job Level: {row['job level']}
Languages: {row['languages']}""", axis=1)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    #embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    #embeddings = VertexAIEmbeddings(model="text-embedding-004")
    embedding_dim = len(embeddings.embed_query("hello world"))
    index = faiss.IndexFlatL2(embedding_dim)

    documents = [Document(page_content=row["combined"], metadata={"title": row["title"], "url": row["Url"]}) for _, row in df.iterrows()]

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    vector_store.add_documents(documents)
    retriever = vector_store.as_retriever()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    system_prompt = """You are a helpful assistant who specializes in recommending SHL assessments to users.
Only recommend assessments found in the retrieved context. Show at most 10 results.
You must include:
1. Title and brief description
2. URL
3. Job Level
4. Languages
5. Duration (Assessment Length)

Context:
{context}

Question: {question}"""
    prompt = ChatPromptTemplate.from_template(system_prompt)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

rag_chain = load_model_and_data()

query = st.text_area("Describe the role you're hiring for:")
if st.button("Recommend Assessments"):
    with st.spinner("Fetching recommendations..."):
        response = rag_chain.invoke(query)
        st.markdown("### ✅ Recommended Assessments")
        st.write(response)
