# Flask-Quiz-App
A website that allows users to create and take quizzes made by other users.  
Made using Flask, Python, and MySQL

## 📚 Features
- 🔐 User registration and login (hashes passwords)
- 🎓 Create custom quizzes (Up to 10 questions per quiz)
- 👥 Take quizzes created by other people
- 😁 Clean and Simple UI
- 🤓 everything sored in a database built from the ground up

## 🧑‍💻 Technologies Used
- VS Code
- MySqL workbench
- MySQL Server

## 🧩 Languages Used
- 🐍 Python
- 🥤 Flask
- 📊 SQL
- 🌐 HTML
- 😎 CSS

# ⚙️ Setup/Installation Instructions

### Step 1. Clone the repository
git clone https://github.com/paul-mac21/Flask-Quiz-App.git
cd Flask-Quiz-App

### Step 2. Set up virtual environment 
in terminal run:  
python -m venv venv  
.\venv\scripts\activate  

### Step 3. Install requirements
in terminal run:  
pip install -r requirements.txt  

### Step 4. Create .env file
Inside this file write:  
DB_HOST=localhost  
DB_USER=your mysql user  
DB_PASSWORD=your password  
DB_NAME=quiz_project  

### Step 5. Create the MySQL database
Simply run the scripts located in the quiz_database file  

### Step 6. Run the app
make sure your virtual environment is active as mentioned in step 2  
enter the following into the terminal:  
python app.py  
follow the link pasted nto terminal( Should look something like "http://127.0.0.1:5000")  

# 🏗️ Potential Additions Being worked on
- option to delete quizzes you made
- option to edit your own quizzes
- user leaderboards

