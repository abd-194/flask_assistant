from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

# Your OpenAI API key
api_key = ""
client = OpenAI(api_key=api_key)

# Your assistant setup
uploaded_file = client.files.create(
    file=open("Data.pdf", "rb"),
    purpose="assistants",
)

assistant = client.beta.assistants.create(
    name="Cedric Chat",
    instructions="You are a fitness expert at Cedric who only have the knowledge of fitness and neutrition related data and your name is Olivia that only answer the user queries based on the data provided and never discuss about the provided document in your response because user can feel uncomfortable with this. If you don't find the relevant data in the documents provided to you, then try to answer the query of user with yourself without talking about the data but never answer the query if it is not related to fitness or neutrition.",
    tools=[{"type": "retrieval"}],
    model="gpt-4-1106-preview",
    file_ids=[uploaded_file.id],
)

thread = client.beta.threads.create()


@app.route("/", methods=["GET", "POST"])
def index():
    response = None

    if request.method == "POST":
        user_input = request.form["user_input"]
        message = client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id,
        )

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                latest_message = messages.data[0]
                response = latest_message.content[0].text.value
                break

    return render_template("index.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)
