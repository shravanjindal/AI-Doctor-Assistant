# **AI-Doctor-Assistant**  

AI-Doctor-Assistant is a smart healthcare assistant designed to provide AI-powered medical insights.  

## **🚀 Getting Started**  

Follow the steps below to set up and run the project on your local system.  

---

## **📌 Prerequisites**  

- **MongoDB** must be installed and running on your system.  
- **Python 3.12** is required for the backend.  
- **Node.js & npm** are required for the frontend.  

---

## **🛠 Backend Setup**  

1️⃣ **Start MongoDB** (Linux)  
```bash
sudo systemctl start mongod
```

2️⃣ **Set Up Python Environment**  
If using **Conda**, create and activate a virtual environment:  
```bash
conda create -n <env_name> python=3.12
conda activate <env_name>
```

3️⃣ **Install Dependencies & Start Backend**  
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## **💻 Frontend Setup**  

1️⃣ **Install Dependencies**  
```bash
cd frontend
npm install
```

2️⃣ **Run the Frontend**  
```bash
npm run dev
```

Now, your AI-Doctor-Assistant should be running locally! 🚀  

<hr />