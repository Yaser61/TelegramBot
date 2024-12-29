import json
from redis_connection import RedisConnection

# Todo: Akışı ve yorumları ingilizce yap. Kullanıcıya response dönüyorsan onları sadece yaz. Onları da dil dosyası oluşturup oradan alabilirsin.

def list_usernames(redis_client):
    """
    Redis'te kayıtlı kullanıcı anahtarlarını al ve kullanıcı adlarını listele.
    """
    keys = redis_client.keys("user:*:chat_history")  # Tüm kullanıcı sohbet geçmişi anahtarlarını al
    usernames = []
    for key in keys:
        user_id = key.split(":")[1]
        firstname_key = f"user:{user_id}:firstname"
        firstname = redis_client.get(firstname_key)
        usernames.append((user_id, firstname.decode('utf-8') if firstname else "Bilinmiyor"))
    return usernames

def get_chat_history(redis_client, username):
    """
    Belirtilen kullanıcı adının sohbet geçmişini al.
    """
    redis_key = f"user:{username}:chat_history"  # Kullanıcının sohbet geçmişi anahtarı
    messages = redis_client.lrange(redis_key, 0, -1)  # Sohbet geçmişini getir
    return [json.loads(message) for message in messages]  # JSON formatında parse et

def main():
    # Redis bağlantısını al
    redis_client = RedisConnection().get_client()

    # Kullanıcı adlarını listele
    usernames = list_usernames(redis_client)

    if not usernames:
        print("Hiçbir kullanıcı bulunamadı.")
        return

    print("Kayıtlı kullanıcılar:")
    for idx, (username, firstname) in enumerate(usernames, start=1):
        print(f"{idx}. {username} ({firstname})")

    # Kullanıcı seçimi
    try:
        selected_idx = int(input("\nBir kullanıcı seçin (numarasını girin): "))
        if selected_idx < 1 or selected_idx > len(usernames):
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Lütfen geçerli bir sayı girin!")
        return

    # Seçilen kullanıcı
    selected_username = usernames[selected_idx - 1][0]
    print(f"\nSeçilen kullanıcı: {selected_username}")

    # Sohbet geçmişini al
    chat_history = get_chat_history(redis_client, selected_username)

    print("\nSohbet geçmişi:")
    if chat_history:
        for entry in chat_history:
            sender = entry.get("sender", "Bilinmiyor")
            message = entry.get("message", "Mesaj yok")
            print(f"{sender}: {message}")
    else:
        print("Bu kullanıcının sohbet geçmişi yok.")

if __name__ == "__main__":
    main()