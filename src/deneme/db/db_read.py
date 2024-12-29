import json
from redis_connection import RedisConnection

def list_usernames(redis_client):
    """
    Get user keys stored in Redis and list usernames.
    """
    keys = redis_client.keys("user:*:chat_history")  # Get all user chat history keys
    usernames = []
    for key in keys:
        user_id = key.split(":")[1]
        firstname_key = f"user:{user_id}:firstname"
        firstname = redis_client.get(firstname_key)
        usernames.append((user_id, firstname.decode('utf-8') if firstname else "unknown"))
    return usernames

def get_chat_history(redis_client, username):
    redis_key = f"user:{username}:chat_history"
    messages = redis_client.lrange(redis_key, 0, -1)
    return [json.loads(message) for message in messages]

def main():
    redis_client = RedisConnection().get_client()

    usernames = list_usernames(redis_client)

    if not usernames:
        print("No users found.")
        return

    print("Registered users:")
    for idx, (username, firstname) in enumerate(usernames, start=1):
        print(f"{idx}. {username} ({firstname})")

    # User choice
    try:
        selected_idx = int(input("\nBir kullanıcı seçin (numarasını girin): "))
        if selected_idx < 1 or selected_idx > len(usernames):
            print("invalid selection!")
            return
    except ValueError:
        print("Please enter a valid number!")
        return

    selected_username = usernames[selected_idx - 1][0]
    print(f"\nSelected user: {selected_username}")

    chat_history = get_chat_history(redis_client, selected_username)

    print("\nchat history:")
    if chat_history:
        for entry in chat_history:
            sender = entry.get("sender", "Bilinmiyor")
            message = entry.get("message", "Mesaj yok")
            print(f"{sender}: {message}")
    else:
        print("This user has no chat history.")

if __name__ == "__main__":
    main()