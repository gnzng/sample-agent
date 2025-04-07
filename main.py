from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_ai import Agent
import openai
from dotenv import load_dotenv
from pathlib import Path
import json
import os
from typing import Dict, Any
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
        print(f"Current sample setup for {filename}:")
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
            You are an agent working on a synchrotron scattering beam line, which mostly measures condensed matter samples. We gater information about a new measurement by user input. 
            The template is:
            {template}.
            If you don't know the answer for a specific field, leave it an empty list and do not add any extra text. ONLY return the filled template in JSON format.

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
            - the temperature is always a list of floats, e.g. [10.0, 20.0], make sure it gets converted to Kelvin
            - if geometry is not specified, set it to an empty string
            - if the puck is not specified, set it to an empty string
            - if the detectors are not specified, set it to an empty list
            - if the energy is not specified, set it to an empty list
            - if the temperature is not specified, set it to an empty list
            - if it is on a membrane it is a transmission geometry measurement

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


def confirm_action(prompt: str, default: bool = False) -> bool:
    """Get user confirmation with yes/no input."""
    valid_yes = ["y", "yes"]
    valid_no = ["n", "no"]
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        response = input(prompt + suffix).strip().lower()
        if not response:
            return default
        if response in valid_yes:
            return True
        if response in valid_no:
            return False
        print("Invalid input. Please enter 'y' or 'n'.")


def get_proposal_id() -> str:
    """Get and confirm proposal ID from user."""
    while True:
        proposal_id = input("Please enter your proposal ID: ").strip()
        if confirm_action(f"You entered proposal ID: {proposal_id}. Is this correct?"):
            return proposal_id
        print("Proposal ID confirmation failed. Please try again.\n")


def initialize_sample_file(proposal_id: str) -> str:
    """Initialize or validate the sample JSON file."""
    filename = f"sample_files/{proposal_id}_samples.json"
    file_path = Path(filename)

    if not file_path.exists():
        with open(file_path, "w") as f:
            json.dump({}, f)
        print(f"Created new sample file: {filename}")
    else:
        print(f"Using existing sample file: {filename}")

    return filename


def process_sample_input(sample_input: str) -> Dict[str, Any]:
    """Process user input through LLM agent and return response."""
    settings = Settings()
    agent = LLMAgent(settings)
    agent.setup()

    request = Request.create(sample_input=sample_input)
    response = agent.run(request)

    # Add validation logic here if needed
    return json.loads(response)


def add_sample(filename: str) -> None:
    """Handle the sample addition process for a single sample."""
    sample_id = get_random_sample_hash()
    print(f"\nAdding sample with ID: {sample_id}")

    sample_input = input(
        "Please enter sample details with the following information:\n"
        "- Sample name\n"
        "- Substrate/membrane\n"
        "- Desired geometries (transmission/reflection)\n"
        "- Puck type (reflection/transmission/holo)\n"
        "- Measurement energy (eV)\n"
        "- Camera/detector (MTE3/Andor)\n"
        "- Measurement temperature (K)\n"
        "- Magnetic field requirement\n"
        "Enter all details separated by commas: "
    ).strip()

    if not sample_input:
        print("Error: No sample details entered. Sample not added.")
        return

    try:
        processed_data = process_sample_input(sample_input)
        processed_data["user_sample_input"] = sample_input
    except Exception as e:
        print(f"Error processing sample input: {e}")
        return

    # Load existing data
    try:
        with open(filename, "r") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Add new sample
    existing_data[sample_id] = processed_data

    # Save updated data
    with open(filename, "w") as f:
        json.dump(existing_data, f, indent=4)

    print(f"Successfully added sample {sample_id} to {filename}")


def main():
    """Main workflow for sample management."""
    print("================================")
    print("=== Sample Management System ===")
    print(("========= for BL7011 =========="))
    print("================================")

    proposal_id = get_proposal_id()
    filename = initialize_sample_file(proposal_id)

    try:
        show_samples(filename)
    except Exception:
        print("")
        print("Starting with fresh sample file.")

    while confirm_action("\nWould you like to add a new sample?", default=True):
        add_sample(filename)

    try:
        print("")
        print("\nFinal sample summary:")
        show_samples(filename)
        print(f"\nProcess completed for proposal {proposal_id}. File saved as {filename}")
    except Exception:
        print("Error displaying final samples or empty sample file.")


if __name__ == "__main__":
    main()
