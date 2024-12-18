import aio_pika
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()

RABBITMQ_URL=os.getenv("RABBITMQ_URL")



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
        # response = await call_mistral_api(prompt)
        response = "sample response"

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
