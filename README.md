prototyping the idea of using an agentic framework in this case `pydantic_ai` and large language models to prepare user input data into structured data about samples.

the idea is to use a sample template very specific to the beam line and use a chatbot-like workflow to add samples to the list. 


Example:
```text
python main.py
What is the your proposal id? 123
Starting the sample adding process for: 123...
You entered proposal ID: 123. Is this correct? (y/yes to confirm)
yes
File 123_samples.json already exists. Samples will be added to the existing file.
Current sample setup for id 123:
+-----------+-----------------+-----------+------------------+------------------+-----------+--------------+-----------------+----------------+
| Sample ID |   Sample name   | Substrate |     Geometry     |       Puck       | Detectors | Energy (eV)  | Temperature (K) | Magnetic Field |
+-----------+-----------------+-----------+------------------+------------------+-----------+--------------+-----------------+----------------+
|    7RZ    | SmCo5 thin film | ['Al2O3'] |  ['reflection']  |  ['reflection']  |  ['MTE3'] | [1000, 1200] |      [300]      |      True      |
|    5T3    |  FeGe thin film |  ['MgO']  | ['transmission'] | ['transmission'] | ['Andor'] |  [700, 800]  |    [300, 400]   |      True      |
+-----------+-----------------+-----------+------------------+------------------+-----------+--------------+-----------------+----------------+
Do you want to add a sample? (y/yes to add, n/no to finish)
yes
Adding sample with ID: 3jf
Please enter the sample details in free text with the following details:
- Sample name
- substrate 
- desired measured geometries (transmission / reflection)
- which puck to use (reflection / transmission / holo) 
- desired measurement energy in eV 
- which camera / detector to use (MTE3 / Andor) 
- desired measurement temperature in Kelvin 
- if a magnetic field should be applied 
10nm Permalloy on SiN membrane, transmission on andor. room temp. no magnetic field. 710eV.
Response from agent:
{
    "Sample name": "10nm Permalloy on SiN membrane",
    "Substrate": [
        "SiN"
    ],
    "Geometry": [
        "transmission"
    ],
    "Puck": [
        "transmission"
    ],
    "Detectors": [
        "Andor"
    ],
    "Energy (eV)": [
        710
    ],
    "Temperature (K)": [
        300
    ],
    "Magnetic Field": false
}
Sample with ID 3jf added to 123_samples.json.
Do you want to add a sample? (y/yes to add, n/no to finish)
no
Sample adding process completed for proposal ID 123, file saved as 123_samples.json.
Current sample setup for id 123:
+-----------+--------------------------------+-----------+------------------+------------------+-----------+--------------+-----------------+----------------+
| Sample ID |          Sample name           | Substrate |     Geometry     |       Puck       | Detectors | Energy (eV)  | Temperature (K) | Magnetic Field |
+-----------+--------------------------------+-----------+------------------+------------------+-----------+--------------+-----------------+----------------+
|    7RZ    |        SmCo5 thin film         | ['Al2O3'] |  ['reflection']  |  ['reflection']  |  ['MTE3'] | [1000, 1200] |      [300]      |      True      |
|    5T3    |         FeGe thin film         |  ['MgO']  | ['transmission'] | ['transmission'] | ['Andor'] |  [700, 800]  |    [300, 400]   |      True      |
|    3jf    | 10nm Permalloy on SiN membrane |  ['SiN']  | ['transmission'] | ['transmission'] | ['Andor'] |    [710]     |      [300]      |     False      |
+-----------+--------------------------------+-----------+------------------+------------------+-----------+--------------+-----------------+----------------+
```

