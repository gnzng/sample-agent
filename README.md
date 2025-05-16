prototyping the idea of using an agentic framework in this case `pydantic_ai` and large language models to prepare user input data into structured data about samples.

the idea is to use a sample template very specific to the beam line and use a chatbot-like workflow to add samples to the list. 


start the server using

```bash
uvicorn server:app --reload
```

and navigate to: [http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html) or whichever IP or port is used by fastapi.

Example:
```text
======================================
=== Sample Management System Agent ===
========= for BLXXX =================
======================================
Please enter your proposal ID (or type 'exit' to quit):
123

You entered proposal ID: 123. Is this correct? [y/N]:

y

Please enter the token for proposal ID 123 (or type 'exit' to quit):

123

Token validated successfully.
Using existing sample file: sample_files/123_samples.json
Current sample setup for sample_files/123_samples.json:
+-----------+-----------------+-----------+--------------+------+-----------+------------------+-----------------+----------------+
| Sample ID |   Sample name   | Substrate |   Geometry   | Puck | Detectors |   Energy (eV)    | Temperature (K) | Magnetic Field |
+-----------+-----------------+-----------+--------------+------+-----------+------------------+-----------------+----------------+
|    782    |  FeGe thin film |    MgO    | transmission |      | ['Andor'] |  [700.0, 800.0]  |  [300.0, 400.0] |      True      |
|    5hP    | SmCo5 thin film |   Al2O3   |  reflection  |      |  ['MTE3'] | [1000.0, 1200.0] |     [300.0]     |      True      |
+-----------+-----------------+-----------+--------------+------+-----------+------------------+-----------------+----------------+

Would you like to add a new sample? [Y/n]:

y

Adding sample with ID: 2jj
Please enter sample details with the following information:
- Sample name
- Substrate/membrane
- Desired geometries (transmission/reflection)
- Puck type (reflection/transmission/holo)
- Measurement energy (eV)
- Camera/detector (MTE3/Andor)
- Measurement temperature (K)
- Magnetic field requirement
Enter all details separated by commas:

10nm Permalloy on SiN membrane, transmission on andor. room temp. no magnetic field. 710eV.
Successfully added sample 2jj to sample_files/123_samples.json

Would you like to add a new sample? [Y/n]:

n


Final sample summary:
Current sample setup for sample_files/123_samples.json:
+-----------+-----------------+--------------+--------------+------+-----------+------------------+-----------------+----------------+
| Sample ID |   Sample name   |  Substrate   |   Geometry   | Puck | Detectors |   Energy (eV)    | Temperature (K) | Magnetic Field |
+-----------+-----------------+--------------+--------------+------+-----------+------------------+-----------------+----------------+
|    782    |  FeGe thin film |     MgO      | transmission |      | ['Andor'] |  [700.0, 800.0]  |  [300.0, 400.0] |      True      |
|    5hP    | SmCo5 thin film |    Al2O3     |  reflection  |      |  ['MTE3'] | [1000.0, 1200.0] |     [300.0]     |      True      |
|    2jj    |  10nm Permalloy | SiN membrane | transmission |      | ['Andor'] |     [710.0]      |     [300.0]     |     False      |
+-----------+-----------------+--------------+--------------+------+-----------+------------------+-----------------+----------------+

Process completed for proposal 123. File saved as sample_files/123_samples.json

```
