# Ordinary Differential Equation Solver

## Overview
This application provides a web-based and graphical interface to solve Ordinary Differential Equations (ODEs) using two methods: Euler's method and Euler-Cauchy method. The solution is built with Django Rest Framework for the backend and Tkinter for the GUI. The application supports creating entries for differential equations and calculating results through a simple and user-friendly interface with hints.

## Features
**Numerical Methods:**
- **Euler Method:** A simple numerical method for solving ODEs by iterating over a series of small steps.
- **Euler-Cauchy Method:** An enhanced version of the Euler method that improves accuracy.  

**Backend (Django Rest Framework):**   
- Handles API requests to create, store, and retrieve differential equation entries.
- Validates user input to ensure accurate calculations.
- Implements caching for the results of repeated calculations.

**Frontend (Tkinter GUI):**   
The graphical interface provides an easy way for users to interact with the solver. The interface consists of two main tabs:
- **Post Tab:** Users can create entries for ODEs by entering initial conditions, step size, and the differential equation.
- **Results Tab:** Users can select an entry from the database, calculate solutions using Euler and Euler-Cauchy methods, view and compare the results.

## Installation
### Backend
To install and run the backend server using Docker, follow the steps below:  
**1. Clone the repository:**  
Firstly, navigate to the target directory using `cd` where you want to store the repository. Then run `git clone`:
``` 
cd /path/to/directory
git clone https://github.com/anastasia-butkevich/DiffSolver.git
cd DiffSolver
```
**2. Create the `.env` file:**  
Create a `.env` file in the project's root directory and add the necessary variables:
```
SECRET_KEY=your_django_secret_key
DEBUG=True  # or False, depending on your environment
ALLOWED_HOSTS=localhost,127.0.0.1 # Add hosts as needed
DB_ENGINE=django.db.backends.sqlite3  
DB_NAME=your_database_name
```
**3.  Build and Run the Docker Container:**  
Build the Docker image:
```
docker buildx build -t diffsolver -f docker/Dockerfile .
```
Run the container:
```
docker run -p 8000:8000 diffsolver
```
Or, if using an `.env` file:
```
docker run --env-file .env -p 8000:8000 diffsolver
```
The backend will now be accessible at `http://localhost:8000/`.

### Frontend

To run the Tkinter GUI:  
**1. Install Dependencies**  
    Ensure you have Python installed. Then, install the required libraries:  
```
pip install requests tkinter matplotlib python-dotenv sympy
```  
**2. Run the Application**  
Navigate to the frontend directory and run the GUI script:
```
python app.py
```
This will launch the graphical user interface.