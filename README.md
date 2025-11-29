# ❄️ NGSR: Next-Gen Smart Refrigerator

NGSR is a smart refrigerator application powered by **Google Cloud Vertex AI (Gemini 2.5 Flash Lite)** and **Firestore**. It helps users manage their fridge inventory, check food freshness, and generate health-compliant recipes based on their personal health profile.

https://docs.google.com/document/d/1Kq5HEEOtqA3jkgUV5wthbRc6qiE3om8TzXSVXXh16wY/edit?usp=sharing

## ✨ Features

*   **👤 User Health Profile**: Define health conditions and dietary restrictions (e.g., Gout, Diabetes, Allergies) which act as rules for the AI.
*   **📸 AI Fridge Analysis**: Upload a photo of your fridge's interior. The AI will:
    *   Detect food items.
    *   Check freshness (Fresh vs. Expiring).
    *   Alert if items are about to expire.
*   **🍲 Smart Recipe Generation**: Suggests recipes that use available ingredients and strictly adhere to the user's health profile.
*   **📊 History Tracking**: Saves all scans and analysis results to Google Cloud Firestore for historical tracking.

## 🛠️ Tech Stack

*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **AI Model**: Google Vertex AI (`gemini-2.5-flash-lite`)
*   **Database**: Google Cloud Firestore
*   **Language**: Python

## 🚀 Setup & Installation

### 1. Prerequisites
*   Google Cloud Platform (GCP) Project with billing enabled.
*   Enable **Vertex AI API** and **Firestore API** in your GCP Console.
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated locally (for local development).

### 2. Clone & Install
```bash
git clone <repository-url>
cd ngsr
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory or set environment variables directly:

```env
GCP_PROJECT_ID="your-gcp-project-id"
GCP_REGION="us-central1"       # Optional, default: us-central1
GCP_DB_NAME="(default)"        # Optional, default: (default)
```

### 4. Run the Application
```bash
streamlit run app.py
```

## 📖 Usage Guide

1.  **Sidebar Setup**: Enter your User ID and select your health conditions/dietary restrictions. Click **"Simpan Profil"**.
2.  **Upload Photo**: Take a picture of your open fridge and upload it in the "Scan Isi Kulkas" section.
3.  **Analyze**: Click **"Analyze with NGSR Brain"**.
4.  **View Results**:
    *   Check the **Inventory** list for items and their status.
    *   See the **Recipe Recommendation** tailored to your health needs.
    *   Read the **Health Logic** to understand why the recipe was chosen.

## ⚠️ Note
Ensure your GCP service account has the necessary permissions (`Vertex AI User`, `Datastore User`) if deploying to Cloud Run or other environments.
