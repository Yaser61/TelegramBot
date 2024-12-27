import asyncio
import json
import logging

from deneme.db.redis_connection import RedisConnection
from deneme.flow2 import TelegramBotFlow


def process_pending_messages(application):
    redis_client = RedisConnection().get_client()

    # Tüm kullanıcı kuyruklarını al
    keys = redis_client.keys("user:*:chat_history")

    for key in keys:
        user_id = key.decode().split(":")[1]  # user ID'yi anahtardan al
        chat_history_raw = redis_client.lrange(key, 0, -1)
        chat_history = [json.loads(message) for message in chat_history_raw]

        for message in chat_history:
            # Mesajı işleyin
            try:
                flow = TelegramBotFlow()
                asyncio.run(flow.kickoff_async(inputs={
                    "user_message": message["message"],
                    "chat_history": chat_history,
                    "physical_features": flow.state.physical_features
                }))

                print(f"Processed message for user {user_id}: {message['message']}")

            except Exception as e:
                logging.error(f"Error processing message for user {user_id}: {e}")