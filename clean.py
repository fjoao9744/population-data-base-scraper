import asyncio
from aiokafka.admin import AIOKafkaAdminClient

async def delete_topic(topic):
    admin = AIOKafkaAdminClient(
        bootstrap_servers="localhost:9092"
    )

    await admin.start()

    try:
        await admin.delete_topics([topic])
        print("Tópico apagado")
    finally:
        await admin.close()

asyncio.run(delete_topic("scraper-topic"))