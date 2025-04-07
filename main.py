from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_ai import Agent
import openai
from dotenv import load_dotenv
from pathlib import Path
import json
import os
from prettytable import PrettyTable

load_dotenv()

cborg_api_key = os.getenv("CBORG_API_KEY")


def load_sample_template():
    """Load and parse the sample_template.json file"""
    template_path = Path(__file__).parent / "sample_template.json"
    with template_path.open("r") as file:
        data = json.load(file)
    return data


def get_random_sample_hash():
    """Generate a 6-character random sample hash using Base58 encoding without external libraries"""
    # Base58 alphabet
    base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    # Generate 4 random bytes
    random_bytes = os.urandom(4)
    # Convert bytes to an integer
    num = int.from_bytes(random_bytes, "big")
    # Encode the integer to Base58
    base58_hash = []
    while num > 0:
        num, remainder = divmod(num, 58)
        base58_hash.append(base58_alphabet[remainder])

    # Return the first 6 characters of the reversed Base58 string
    return ''.join(reversed(base58_hash))[:3]


def show_samples(filename):
    # just view the current sample setup file as a table
    with open(filename, "r") as file:
        data = json.load(file)
        print(f"Current sample setup for id {proposal_id}:")
        # Create a PrettyTable object with headers
        headers = ["Sample ID"] + list(next(iter(data.values())).keys())
        headers.remove("user_sample_input")  # Exclude "user_sample_input" from headers
        table = PrettyTable(headers)

        # Add rows to the table
        for sample_id, sample_data in data.items():
            row = [sample_id] + [sample_data.get(key, "") for key in headers[1:]]
            table.add_row(row)

        # Print the table
        print(table)


class Settings(BaseSettings):
    """Configuration settings for the AI workflow"""
    cborg_api_key: str = cborg_api_key
    base_url: str = "https://api.cborg.lbl.gov"
    model: str = "openai/gpt-4o-mini"


class Request(BaseModel):
    """Request object for the AI agent"""
    prompt: str

    @classmethod
    def create(cls, sample_input: str):
        """Create a Request object with the given sample input"""
        template = json.dumps(load_sample_template())
        prompt = (
            f"""
            You are an agent working on a synchrotron scattering beam line, which mostly measures condensed matter samples. We gater information about a new measurement by user input. The template is: {template}.  If you don't know the answer for a specific field, leave it an empty list and do not add any extra text. ONLY return the filled template in JSON format.

            Consider the following things:
            - when no magnetic field is applied the field should be set to false. for any other value, it should be set to true.
            - only reply in raw text, do not add any extra text.
            - Magnetic Field should not be a list, but a boolean value.
            - if room temperature or 'rt' is mentioned, set the temperature to 300K
            - if no magnetic field is specified, set the field to false
            - the substrate can also be a membrane, use your physics knowledge to correctly identify the substrate and sample name. look out for dividing keywords like 'on' or 'in' or 'with' or 'of'
            - only use one string for the geometry, e.g. "transmission" or "reflection"
            - only use one string for the puck, e.g. "reflection" or "transmission" or "holo"
            - the detectors are always a list of strings, e.g. ["MTE3", "Andor"]
            - the energy is always a list of floats, e.g. [10.0, 20.0] and in electron volts, make sure you convert keV to eV
            - the temperature is always a list of floats, e.g. [10.0, 20.0]
            - if geometry is not specified, set it to an empty string
            - if the puck is not specified, set it to an empty string
            - if the detectors are not specified, set it to an empty list
            - if the energy is not specified, set it to an empty list
            - if the temperature is not specified, set it to an empty list

            Use the following user input to fill out the template. The user input is: {sample_input}.
            """
        )
        return cls(prompt=prompt)


class OpenAIConfig:
    """Configuration for the OpenAI client using the Cborg API"""
    def __init__(self, settings: Settings):
        self.client = openai.Client(
            api_key=settings.cborg_api_key,
            base_url=settings.base_url
        )


class LLMAgent(Agent):
    """Pydantic AI agent for getting the current time"""
    settings: Settings
    config: OpenAIConfig

    def __init__(self, settings: Settings):
        """Initialize the agent with settings"""
        self.settings = settings

    def setup(self):
        """Initialize the OpenAI client access Cborg API"""
        self.config = OpenAIConfig(self.settings)

    def run(self, request: Request):
        """Execute the time query"""
        response = self.config.client.chat.completions.create(
            model=self.settings.model,
            messages=[
                {"role": "user", "content": request.prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    # walk throught the sample adding process:
    proposal_id = input("What is the your proposal id? ")

    # Verify the proposal ID input
    print(f"You entered proposal ID: {proposal_id}. Is this correct? ([y]es to confirm)")
    confirmation = input().strip().lower()
    if confirmation not in ["y", "yes"]:
        print("Error: Proposal ID confirmation failed. Exiting. Start process again, with a valid proposal ID.")
        exit(1)
    print(f"Starting the sample adding process for: {proposal_id}...")
    # Create an empty JSON file with the proposal_id as part of the filename
    filename = f"{proposal_id}_samples.json"
    if Path(filename).exists():
        print(f"File {filename} already exists. Samples will be added to the existing file.")
    else:
        with open(filename, "w") as file:
            json.dump({}, file)
        print(f"Created sample setup file: {filename}")

    try:
        show_samples(filename)
    except Exception:
        print("No existing samples found. Starting with an empty file.")

    adding_samples = True
    while adding_samples:
        print("Do you want to add a sample? ([y]es to add, [n]o to finish)")
        confirmation = input().strip().lower()
        if confirmation in ["y", "yes"]:
            sample_id = get_random_sample_hash()
            print(f"Adding sample with ID: {sample_id}")
            sample_input = input("Please enter the sample details in free text with the following details:\n"
                                 "- sample name\n"
                                 "- substrate or membrane \n"
                                 "- desired measured geometries (transmission / reflection)\n"
                                 "- which puck to use (reflection / transmission / holo) \n"
                                 "- desired measurement energy in eV \n"
                                 "- which camera / detector to use (MTE3 / Andor) \n"
                                 "- desired measurement temperature in Kelvin \n"
                                 "- if a magnetic field should be applied \n"
                                 )
            # Create a request object with the sample input
            request = Request.create(sample_input=sample_input)
            # Create a request object with the sample input
            request = Request(prompt=request.prompt)
            # Initialize settings and agent
            settings = Settings()
            agent = LLMAgent(settings)
            agent.setup()
            # Run the agent with the request
            response = agent.run(request)
            print("Response from agent:")
            print(json.dumps(json.loads(response), indent=4))
            # Add the sample ID to the response
            response = json.loads(response)

            # TODO implement a check if the response has valid fields.

            response["user_sample_input"] = sample_input
            new_sample_item = {sample_id: response}
            # Load the existing data from the file
            with open(filename, "r") as file:
                existing_data = json.load(file)
            # Update the data with the new sample item
            existing_data.update(new_sample_item)
            # Save the updated data back to the file
            with open(filename, "w") as file:
                json.dump(existing_data, file, indent=4)
            print(f"Sample with ID {sample_id} added to {filename}.")

        elif confirmation in ["n", "no"]:
            adding_samples = False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    print(f"Sample adding process completed for proposal ID {proposal_id}, file saved as {filename}.")
    show_samples(filename)
