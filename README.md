# Telegram Bot

This project is a Telegram bot that processes user messages and generates responses based on the content of the messages. The bot can generate text, photo, and voice responses.

## Features

- **Message Handling**: Receives and processes user messages.
- **Decision Making**: Determines whether a photo or voice response is needed based on the user's message.
- **Response Generation**: Generates appropriate responses (text, photo, voice) and sends them to the user.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up environment variables:

## Usage

1. Run the bot:
    ```sh
    python flow.py
    ```

2. The bot will start and listen for incoming messages.

## Code Overview

### `flow.py`

- **`handle_message`**: Handles incoming messages, updates chat history, and initiates the flow.
- **`TelegramBotFlow`**: Manages the flow of the bot, including decision making and response generation.
  - **`decides`**: Determines if a photo or voice response is needed.
  - **`generate_response_withphoto`**: Generates a response with a photo.
  - **`generate_response_withoutphoto`**: Generates a response without a photo.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.