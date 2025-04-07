from main import Request, Settings, LLMAgent
import pytest
import json
from typing import List


@pytest.mark.parametrize(
    "sample_input",
    [
        "text_examples/sample.txt",
        "text_examples/sample.txt",
        "text_examples/sample2.txt",
        "text_examples/sample3.txt",
        "text_examples/sample4.txt",
        "text_examples/sample5.txt",
        "text_examples/sample6.txt",
        "text_examples/sample7.txt",
    ],
)
def test_templater_response(sample_input):
    with open(sample_input, "r") as file:
        sample_input = file.read()

    request = Request.create(sample_input=sample_input)

    # Create a request object with the sample input
    request = Request(prompt=request.prompt)
    # Initialize settings and agent
    settings = Settings()
    agent = LLMAgent(settings)
    agent.setup()
    # Run the agent with the request
    response = agent.run(request)

    print(f"Response from agent for {sample_input}: \n{response}")
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"

    # string should be valid JSON
    try:
        json.loads(response)
    except json.JSONDecodeError:
        assert False, "Response is not valid JSON"

    # Check if the response contains the expected keys
    response_json = json.loads(response)
    keys = list(response_json.keys())
    assert ['Sample name', 'Substrate', 'Geometry', 'Puck', 'Detectors', 'Energy (eV)', 'Temperature (K)', 'Magnetic Field'] == keys

    # check if the have the expected values
    assert isinstance(response_json["Sample name"], str), "Sample name should be a string"
    assert isinstance(response_json["Substrate"], str), "Substrate should be a string"
    assert isinstance(response_json["Geometry"], str), "Geometry should be a string"
    assert isinstance(response_json["Puck"], str), "Puck should be a string"
    assert isinstance(response_json["Detectors"], List), "Detectors should be a string"
    assert isinstance(response_json["Energy (eV)"], List), "Energy should be a float"
    assert isinstance(response_json["Temperature (K)"], List), "Temperature should be a float"
    assert isinstance(response_json["Magnetic Field"], bool), "Magnetic Field should be a boolean"

    # Check if the response lists contains the expected values
    energy_values = response_json["Energy (eV)"]
    temperature_values = response_json["Temperature (K)"]
    if len(energy_values) > 0:
        assert all(isinstance(value, (int, float)) for value in energy_values), "Energy values should be numbers"
        assert all(10 < value < 10000 for value in energy_values), "All Energy (eV) values should be between 10 and 10000"
    if len(temperature_values) > 0:
        assert all(isinstance(value, (int, float)) for value in temperature_values), "Temperature values should be numbers"
        assert all(0 < value < 1000 for value in temperature_values), "All Temperature (K) values should be between 0 and 10000"

    # Check the detectors list, should only include MTE3 or/and Andor
    detectors = response_json["Detectors"]
    if len(detectors) > 0:
        assert all(detector in ["MTE3", "Andor"] for detector in detectors), "Detectors should be MTE3 or Andor"


if __name__ == "__main__":
    test_templater_response()
