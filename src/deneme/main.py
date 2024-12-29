#!/usr/bin/env python
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# Todo: bunu kullanmıyorsak sil.

def run():
    """
    Run the crew.
    """
    inputs = {
        "conversation_context": {
            "user_message": "Bana matematik sorusu sor?"
        }
    }


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        #"topic": "AI LLMs"
    }

def replay():
    """
    Replay the crew execution from a specific task.
    """

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        #"topic": "AI LLMs"
    }