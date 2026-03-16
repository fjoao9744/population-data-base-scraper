from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio, json

async def start_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',  # endereço do broker Kafka
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    return producer

async def send_to_kafka(producer, topic, data):
    await producer.send_and_wait(topic, data)


async def process_message(msg):
    data = json.loads(msg.value)
    # Aqui você roda qualquer função de processamento
    print("Processando:", data)
    # Ex: salvar no banco, análise, etc.

async def consume():
    consumer = AIOKafkaConsumer(
        "scraper-topic",
        bootstrap_servers="localhost:9092",
        group_id="processing-group",
        auto_offset_reset="earliest"
    )
    await consumer.start()

    try:
        async for msg in consumer:
            asyncio.create_task(process_message(msg))
    finally:
        await consumer.stop()

# Rodar em outro terminal ou processo
# asyncio.run(consume())