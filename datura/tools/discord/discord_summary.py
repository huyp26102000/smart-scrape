from openai import AsyncOpenAI
from datura.protocol import ScraperTextRole

client = AsyncOpenAI(timeout=60.0)

SYSTEM_MESSAGE = """
As a Discord data analyst, your task is to provide users with a clear and concise answer derived from the given Discord chat conversation and the user's query.

Output Guidelines (Tasks):
1. Analyze the user's prompt and the provided Discord chat messages (including replies) and write a well-rounded answer that addresses the user's query.

<OutputExample>
**Discord Search Summary:**

To register Bittensor wallet address, you can visit following link: [Create Bittensor Wallet](https://docs.bittensor.com/getting-started/wallets).
Once you have registered your wallet address, you can start earning rewards by participating in the Bittensor network. 
</OutputExample>

Operational Rules:
1. No Discord Data Scenario: If no Discord data is provided, inform the user that there are no related chat messages from users.
2. Emphasis on Critical Issues: Focus on and clearly explain any significant issues or points of interest that emerge from the analysis.
3. Seamless Integration: Avoid explicitly stating "Based on the provided Discord data" in responses. Assume user awareness of the data integration process.
4. Structure Responses: Separate responses into sections for easy reading.
5. User-Friendly Language: Do not return text like <UserPrompt>; make responses easy to understand for any user.
6. Use Markdown: Make headers bold using Markdown
7. Provide Links: Include links to relevant resources or information if necessary
"""


async def summarize_discord_data(
    prompt: str,
    model: str,
    filtered_messages,
):
    content = f"""
    In <UserPrompt> provided User's prompt (Question).
    In <DiscordData>, Provided Discord API fetched data.

    <UserPrompt>
    {prompt}
    </UserPrompt>

    <DiscordData>
    {filtered_messages}
    </DiscordData>
    """

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": content},
    ]

    res = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        stream=True,
    )

    return res, ScraperTextRole.DISCORD_SUMMARY


def prepare_message(message):
    return {
        "content": message.get("content", ""),
        "channel": message.get("channel", ""),
        "author": message.get("author", ""),
    }


def prepare_messages_data_for_summary(messages):
    body = messages.get("body", [])

    # Error handling
    if isinstance(body, str):
        return []

    normalized_messages = []

    for message in body:
        normalized_messages.append(
            {
                **prepare_message(message),
                "replies": [
                    prepare_message(reply) for reply in message.get("replies", [])
                ],
                "possible_replies": [
                    prepare_message(reply)
                    for reply in message.get("possible_replies", [])
                ],
            }
        )

    return normalized_messages
