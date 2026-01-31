Project Name: The Air Pollution AQI Website
Team Members: A Bindu, A Divya, Aishwarya T, Ankitha Siri Maddani
Guide: Mrs. Madhuri Akki
Institution: Ballari Institute of Technology & Management
Course: Computer Science and Engineering
Academic Year: 2026

--------------------------------------------------
PROJECT DESCRIPTION
--------------------------------------------------
AQI WEB is a web-based Air Quality Index (AQI) application
developed using Python Flask. The application allows users
to register, log in, search for city-wise AQI information,
and view pollution-related awareness content.

The project also supports voice-based city search using
speech recognition and fetches AQI data through external APIs.

--------------------------------------------------
PROJECT DIRECTORY STRUCTURE
--------------------------------------------------
AQI_WEB(F)/
│
├── static/
│   ├── about.jpg
│   └── brand-awareness.jpg
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── awarness.html
│   ├── login.html
│   ├── register.html
│   ├── predict.html
│   └── result.html
│
├── app.py(backend)
├── aqi.db
├── requirements.txt
└── README.txt

--------------------------------------------------
SYSTEM REQUIREMENTS
--------------------------------------------------
Operating System:
- Windows / Linux / macOS

Software Requirements:
- Python version 3.8 or above
- Web Browser (Google Chrome recommended)

--------------------------------------------------
REQUIRED LIBRARIES
--------------------------------------------------
The following Python libraries are required to run this project:

- Flask
- requests
- speechRecognition

These libraries are listed in the requirements.txt file.

--------------------------------------------------
INSTALLATION & EXECUTION STEPS
--------------------------------------------------
1. Copy the complete project folder from the DVD to your PC.
2. Open Command Prompt / Terminal.
3. Navigate to the project directory:
   cd AQI_WEB(F)
4. Install required libraries using:(On Windows)
   python -m pip install -r requirements.txt
5. Run the Flask application using:
   python app.py
6. Open a web browser and go to:
   http://127.0.0.1:5000/

--------------------------------------------------
USAGE INSTRUCTIONS
--------------------------------------------------
- Register a new user using the Register page.
- Log in using valid credentials.
- Enter a city name to check AQI details.
- Use the microphone button for voice-based city search.
- View AQI results and awareness pages.

--------------------------------------------------
DATABASE DETAILS
--------------------------------------------------
Database Used: SQLite
Database File: aqi.db

The database stores user login and registration information.

--------------------------------------------------
NOTES
--------------------------------------------------
- Internet connection is required to fetch AQI data.
- Voice search works best in Google Chrome.
- Ensure microphone permission is enabled in the browser.

--------------------------------------------------
DECLARATION
--------------------------------------------------
This project is developed for academic purposes and is
submitted as part of coursework requirements.
