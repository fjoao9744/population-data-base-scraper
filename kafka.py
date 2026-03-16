from aiokafka import AIOKafkaProducer
import json

async def start_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    return producer

async def send_to_kafka(producer, topic, data):
    await producer.send_and_wait(topic, data)
