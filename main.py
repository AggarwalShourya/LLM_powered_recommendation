import pandas as pd
import faiss
import sentence_transformers
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

load_dotenv() 
api_key = os.getenv("GOOGLE_API_KEY")

df=pd.read_csv("Data.csv")
#print(len(df))

df["combined"] = df.apply(lambda row: f"""Title: {row['title']}
Description: {row['description']}
Assessment Length: {row['Assesment Length']}
Job Level: {row['job level']}
Languages: {row['languages']}""", axis=1)

#EMBEDDING_MODEL_NAME = "thenlper/gte-small"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

documents = [
    Document(page_content=row["combined"], metadata={"title": row["title"], "url": row["Url"]})
    for _, row in df.iterrows()
]

embedding_dim = len(embeddings.embed_query("hello world"))
index = faiss.IndexFlatL2(embedding_dim)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)
# Add documents to FAISS
vector_store.add_documents(documents)
retriever = vector_store.as_retriever()
#print(retriever)
query=""" I am hiring for an engineer with: 

 Relevant experience in AI/ML - NLP, speech processing, and computer vision. 
 Proficiency in Python and ML frameworks such as TensorFlow, PyTorch, & OpenAI APIs. 
 Good knowledge of ML theory deep learning, and statistical modeling. 

 Familiarity with Generative AI (LLMs & RAG). 
 Experience in prototyping and deploying AI. 
 Agile and proactive thinking.  """
relevant_docs = retriever.get_relevant_documents(query)
for i, doc in enumerate(relevant_docs, 1):
    print(f"--- Document {i} ---")
    print("Title:", doc.metadata.get("title", "N/A"))
    print("URL:", doc.metadata.get("url", "N/A"))
    print("Content:\n", doc.page_content)
    print("\n" + "-"*40 + "\n")


#llm = init_chat_model("gemini-2.0-flash-001", model_provider="google_vertexai")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
system_prompt="""" You are a helpful assistant who specializes in recommending SHL assessments to users. 
    Only recommend assessments found in the retrieved context. Show at most 10 results.You need to return the following details to the user:
    1) The title and a brief description of the assessment.
    2) The URL of the assesment.
    3) Job Level
    4) Language
    5) And the Duration of exam(make sure it strictly adheres to the timeline)
    
    Don't try to make up an answer.
Context:
{context}

Question: {question}"""
prompt = ChatPromptTemplate.from_template(system_prompt)
#template = ChatPromptTemplate.from_messages([
 #  Only recommend assessments found in the retrieved context. Show at most 10 results."""),
  #  ("human", """User Query: {query}\n\nRelevant Documents:\n{context}""")
#])

"""question_answer_chain = create_stuff_documents_chain(llm, template)
chain = create_retrieval_chain(retriever, question_answer_chain)"""
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
query= """I am hiring for an engineer with: 

 Relevant experience in AI/ML - NLP, speech processing, and computer vision. 
 Proficiency in Python and ML frameworks such as TensorFlow, PyTorch, & OpenAI APIs. 
 Good knowledge of ML theory deep learning, and statistical modeling. 

 Familiarity with Generative AI (LLMs & RAG). 
 Experience in prototyping and deploying AI. 
 Agile and proactive thinking.  """
response = rag_chain.invoke(query)
print(f"Query: {query}")
print(f"Response: {response}")
