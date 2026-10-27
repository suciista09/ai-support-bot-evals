from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

reply = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Halo! Balas dalam satu kalimat: apa itu TokoKita?"}],
)

text = next(b.text for b in reply.content if b.type == "text")
print(text)
print(reply.usage)