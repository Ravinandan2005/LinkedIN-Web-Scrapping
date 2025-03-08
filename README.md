# 🚀 LinkedIn Web Scraper

## 📌 Project Overview
This project is a **LinkedIn Connection Scraper** built using **Python and Selenium** to automate the process of extracting LinkedIn profile data from your connections. The extracted data is stored in an **SQLite database** for further analysis and reference.

## 🛠️ Features
- ✅ **Automated LinkedIn Login** using Selenium WebDriver
- ✅ **Extracts Profile Information** (Name, Headline, About, Experience, Education, Skills, and Projects)
- ✅ **Stores Data Efficiently** in an SQLite database
- ✅ **Handles Pagination & Scrolling** to scrape multiple connections
- ✅ **Avoids Duplicates** using database constraints

## 📂 Project Structure
```
📁 linkedin-scraper
├── 📄 main.py               # Main script for scraping
├── 📄 login.txt           # Script to create and manage SQLite database
└── 📄 README.md            # Project documentation
```

## 🏗️ Installation & Setup
### 🔹 Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- Google Chrome & ChromeDriver
- Selenium
- SQLite3 (built into Python)

### 🔹 Install Dependencies
```sh
pip install -r requirements.txt
```

### 🔹 Setup ChromeDriver
Make sure ChromeDriver is installed and added to your **system path** or place it in the project directory.

### 🔹 Run the Scraper
```sh
python main.py
```

## 🔒 Authentication
> **Important:** Never hardcode your LinkedIn credentials in the script. Use **environment variables** or a config file that is not tracked by Git.

## 📊 Data Stored in SQLite
The scraped LinkedIn data is structured into tables:
- `profiles` (stores name, headline, about info)
- `experience` (stores job history)
- `education` (stores degrees & institutions)
- `skills` (stores listed skills)
- `projects` (stores project details)

## 🚀 Future Improvements
- 🔹 Implement **Multi-Threading** to speed up scraping
- 🔹 Add **Headless Browser Mode** for stealthy scraping
- 🔹 Store data in **MySQL/PostgreSQL** instead of SQLite
- 🔹 Implement **Cloud Integration** (AWS/GCP) for better scalability

## ⚠️ Disclaimer
This project is for **educational purposes only**. Scraping LinkedIn may **violate its Terms of Service**, and excessive scraping can lead to account restrictions. Use it responsibly!

## Contributions

Feel free to fork this repository, submit issues, or send pull requests. Contributions are welcome!

## If you find this project helpful, please consider giving it a ⭐ and forking it! 🙏

## 📬 Connect with Me
💡 Have suggestions or issues? Feel free to **open an issue** or reach out!

🔗 **GitHub**: [@Ravinandan2005](https://github.com/ravinandan2005)  
🔗 **LinkedIn**: [J N Ravinandan](https://linkedin.com/in/ravinandan2005)


