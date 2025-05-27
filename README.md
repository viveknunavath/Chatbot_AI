# 🤖 Smart E-Commerce Negotiation Chatbot

This project is a **Flask-based AI-powered chatbot** designed for a smart e-commerce platform. It enables users to:

* Browse products
* Negotiate prices using **text** or **voice**
* Place orders
* Post and view reviews with **sentiment analysis**
* Leverage a modern **PostgreSQL backend**

---

## 🚀 Live Demo

[🔗 Click here to view the live app](https://chatbot-ai-y1kp.onrender.com)

> ⚠️ Please remember to **logout** after use. Data for reviews and orders is automatically deleted upon logout to optimize storage.

---

## 📂 Features

### 🔍 Browse Products

* Displays products from `ecommerce.csv`
* Includes name, description, and price

### 🤖 Smart Negotiation

* Users can negotiate prices via text or voice
* Uses basic discount logic with predefined limits
* Responds with synthesized audio via Google Text-to-Speech

### 🛒 Place Orders

* Final price is stored post negotiation
* Orders are timestamped and user-specific

### 📝 Post Review

* User submits review text
* Sentiment analyzed using **VADER** (Positive, Negative, Neutral)
* Stored in PostgreSQL

### 👁️ View Reviews & Orders

* View your own reviews and orders
* Admin-style table format with Tailwind styling

### 🔐 Authentication

* Signup/Login system
* Stores user data securely in PostgreSQL

### 🧼 Automatic Cleanup

* Voice recordings are **not saved permanently**
* Temp audio files are **deleted immediately** after processing
* Reviews and orders are deleted after logout

---

## 🛠️ Tech Stack

| Layer         | Technology                    |
| ------------- | ----------------------------- |
| Backend       | Python, Flask                 |
| Frontend      | HTML, Tailwind CSS            |
| AI Components | VADER (NLP), gTTS, SR         |
| Database      | PostgreSQL (hosted on Render) |
| Deployment    | Render                        |

---

## 🗃️ Dataset

* Product data is loaded from `Dataset/ecommerce.csv`
* Negotiation price is precomputed and loaded from `model_cleaned.csv`

---

## 🔒 Security & Constraints

* Render PostgreSQL Free Plan (1 GB storage)
* User data is cleaned up to stay within usage limits
* ffmpeg is used for audio conversion (voice chat)
* Compatible with browsers that support WebM audio recording

---

## ⚙️ Setup Instructions

### 📁 Clone the Repository

```bash
git clone https://github.com/viveknunavath/Chatbot_AI.git
cd Chatbot_AI
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 🗄️ Set up PostgreSQL

Use the credentials from Render PostgreSQL dashboard. Update `get_db_connection()` in `Main.py` accordingly.

### ▶️ Run the Flask App

```bash
python Main.py
```

Then open `http://localhost:10000` in your browser.

---

## 👤 Author

**Vivek Nunavath**

For questions or collaboration, connect via GitHub or email.

---

## 📝 License

This project is licensed under the MIT License.

---

Thank you for using this smart e-commerce negotiation assistant! ✨
