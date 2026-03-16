from aiokafka import AIOKafkaConsumer
import json
import asyncio
import aiosqlite

queue = asyncio.Queue()

async def insert_batch(conn, batch):
    placeholders = ",".join(["(?, ?)"] * len(batch))

    query = f"""
    INSERT INTO celulares (name, price)
    VALUES {placeholders}
    """

    await conn.executemany(
        "INSERT INTO celulares (tittle, price) VALUES (?, ?)",
        batch
    )

async def database_worker(conn):
    while True:
        batch = []
    
        while len(batch) < 50:
            try:
                item = await asyncio.wait_for(queue.get(), 0.2)
                batch.append(item)
                print(item)
                
            except asyncio.TimeoutError:
                pass

        if not batch:
            continue

        await insert_batch(conn, batch)
        await conn.commit()

        for _ in batch:
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
    for _ in range(3): # workers
        asyncio.create_task(database_worker(conn))

    try:
        async for msg in consumer:

            data = json.loads(msg.value)

            await queue.put((data["tittle"], data["price"]))

    finally:
        await conn.close()
        await consumer.stop()

asyncio.run(consume())

