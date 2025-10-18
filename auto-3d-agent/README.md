# Auto 3D Agent

## Overview
The Auto 3D Agent is a fully automated system designed to generate 3D models based on user-defined specifications. By utilizing various input types such as text descriptions, images, and videos, the agent retrieves additional data from online sources to enhance the model generation process. The final output is optimized for CAD applications.

## Features
- **Input Handling**: Supports text, image, and video inputs for model specifications.
- **Data Retrieval**: Gathers additional information from sources like GitHub, Reddit, and web searches to improve model accuracy.
- **3D Model Generation**: Utilizes advanced algorithms to create detailed 3D models.
- **CAD Export**: Exports generated models in formats compatible with CAD software.

## Project Structure
```
auto-3d-agent
├── src
│   ├── app.py                # Main entry point of the application
│   ├── ingestion              # Module for processing input data
│   ├── retriever              # Module for fetching additional data
│   ├── generator              # Module for generating 3D models
│   ├── cad_export             # Module for exporting models to CAD formats
│   ├── pipelines              # Main pipeline logic
│   └── utils                 # Utility functions
├── tests                      # Unit tests for the application
├── configs                    # Configuration files
├── scripts                    # Scripts for running the application
├── Dockerfile                 # Docker image instructions
├── .gitignore                 # Git ignore file
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/leifi9/K1C-Board.git
   ```
2. Navigate to the project directory:
   ```bash
   cd K1C-Board/auto-3d-agent
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** Blender and FreeCAD must be installed separately (see requirements.txt for details).

## Usage
To run the Auto 3D Agent, execute the following script:
```
bash scripts/run_agent.sh
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.