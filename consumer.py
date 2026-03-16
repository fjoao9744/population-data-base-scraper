from aiokafka import AIOKafkaConsumer
import json
import asyncio
import aiosqlite

queue = asyncio.Queue()

async def database_worker(conn):

    while True:
        data = await queue.get()

        await conn.execute(
            "INSERT INTO celulares (tittle, price) VALUES (?, ?)",
            (data["tittle"], data["price"])
        )

        await conn.commit()

        queue.task_done()


async def consume():

    consumer = AIOKafkaConsumer(
        "scraper-topic",
        bootstrap_servers="localhost:9092",
        group_id="processing-group",
        auto_offset_reset="earliest"
    )

    await consumer.start()

    conn = await aiosqlite.connect("database.db")

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS celulares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tittle TEXT,
            price REAL
        )
    """)

    await conn.commit()

    asyncio.create_task(database_worker(conn))

    try:
        async for msg in consumer:

            data = json.loads(msg.value)

            await queue.put(data)

    finally:
        await consumer.stop()


asyncio.run(consume())