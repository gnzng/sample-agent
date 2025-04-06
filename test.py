from main import Request, Settings, TimeAgent


def test_templater_response():
    with open("text_examples/sample.txt", "r") as file:
        sample_input = file.read()

    request = Request.create(sample_input=sample_input)

    # Create a request object with the sample input
    request = Request(prompt=request.prompt)
    # Initialize settings and agent
    settings = Settings()
    agent = TimeAgent(settings)
    agent.setup()
    # Run the agent with the request
    response = agent.run(request)
    print(f"Response from agent: {response}")


if __name__ == "__main__":
    test_templater_response()
