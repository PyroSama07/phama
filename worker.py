from langchain.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import aio_pika
import asyncio
import json
load_dotenv()

QDRANT_URL=os.getenv('QDRANT_URL')
# RABBITMQ_URL = os.getenv('RABBITMQ_URL')
RABBITMQ_URL="amqp://guest:guest@localhost/"

model_name = 'l3cube-pune/punjabi-sentence-similarity-sbert'
embeddings = HuggingFaceEmbeddings(
    model_name=model_name)

client = QdrantClient(QDRANT_URL,timeout=60)
COLLECTION_NAME="phama"

vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

retriever = vectorstore.as_retriever(search_kwargs={'k':3})

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """ਤੁਸੀਂ ਕਾਲ ਸੈਂਟਰ ਵਿੱਚ ਇੱਕ ਕਰਮਚਾਰੀ ਹੋ। ਆਪਣੇ ਖੁਦ ਦੇ ਗਿਆਨ ਅਤੇ ਹੇਠਾਂ ਦਿੱਤੇ ਤਿੰਨ ਸੰਦਰਭਾਂ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਸਵਾਲ ਦਾ ਇੱਕ ਹੀ ਸੰਯੁਕਤ ਜਵਾਬ ਪ੍ਰਦਾਨ ਕਰੋ।
            ਸੰਦਰਭ:
            {context}
            """,
        ),
        ("human", "{question}"),
    ]
)

llm = ChatMistralAI(
    model="mistral-large-latest",temperature=0
)

def get_answer(question):
    # Retrieve multiple relevant documents
    contexts = retriever.get_relevant_documents(question)

    # Prepare a structured string for contexts
    formatted_contexts = "\n\n".join(
        [f"ਸੰਦਰਭ {i + 1}: {context.page_content}" for i, context in enumerate(contexts)]
    )

    # Prepare the chain with the formatted contexts and question
    rag_chain = (
        RunnableMap({
            "context": lambda x: formatted_contexts, 
            "question": lambda x: question
        })
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Run the chain and get the result
    answer = rag_chain.invoke({})
    return answer

async def on_message(message: aio_pika.IncomingMessage):
    """Callback to process incoming RabbitMQ messages."""
    async with message.process():
        payload = json.loads(message.body)
        print(f"Received payload: {payload}")
        prompt = payload.get("prompt")
        reply_to = payload.get("reply_to")
        correlation_id = message.correlation_id

        print(f"Received prompt: {prompt}")
    
        # Call Mistral API for chatbot response
        response = get_answer(prompt)
        # response = "sample response"

        # Send response back to the reply queue
        await send_response(reply_to, response, correlation_id)

async def send_response(reply_to, response, correlation_id):
    """Publishes the chatbot response to the reply queue."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"response": response}).encode(),
                correlation_id=correlation_id,
            ),
            routing_key=reply_to,
        )
        print(f"Sent response: {response}")
        print(f"Reply To: {reply_to}, Correlation ID: {correlation_id}")

async def main():
    """Connect to RabbitMQ and start consuming messages."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("chat_requests")
        print("Waiting for chat requests...")
        await queue.consume(on_message)
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())



