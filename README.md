# clockify-monday-ETL-template

This repository contains Python scripts that enable the extraction, transformation, and loading of data between Clockify and Monday.com. The main use case for these scripts is to automate the process of retrieving data from Clockify, processing it, and then updating fields within a dashboard on a Monday.com board.

## Getting Started

Clone this repository to your local machine to get started. You will need Python 3.7 or later installed. We also recommend setting up a virtual environment to manage the dependencies.

```
git clone https://github.com/username/clockify-monday-ETL-template.git
cd clockify-monday-ETL-template
```

## Installation

We recommend using a virtual environment to manage your project's dependencies. To create a virtual environment, run:

```
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Once you have your virtual environment set up and activated, install the dependencies:

```
pip install -r requirements.txt
```

## Usage

Before running the scripts, make sure to set up the `config.py` file with your specific Clockify and Monday.com configurations, like API keys, Workspace ID, Board ID, etc. 

The repository consists of two main scripts:

1. `DetailDashboardTemplate.py`
2. `OverviewDashboardTemplate.py`

You can run these scripts separately according to your requirements or you can use the `main.py` script to run both of them:

```
python main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue on this GitHub repository.

## Disclaimer

This project is provided as-is, and it is not officially associated with either Clockify or Monday.com.

## Acknowledgements

This project would not be possible without the APIs and documentation provided by both Clockify and Monday.com.
