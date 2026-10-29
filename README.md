# 🤖 SmartFAQ

SmartFAQ is an intelligent FAQ chatbot...

## 🚀 Live Demo.

**🔗 [Launch SmartFAQ →](https://smartfaq-7efn2egsyxnq53gj7nffay.streamlit.app/)**

> 💡 No installation required. Open the link and start asking questions!

## Intelligent Student Support Assistant

SmartFAQ is an AI/NLP-based FAQ chatbot designed to answer common college and university student questions.

The system works locally using:

- Python
- NLTK
- Scikit-learn
- TF-IDF
- Cosine Similarity
- Pandas
- NumPy
- Streamlit

No OpenAI API or paid API is required.

---

# Features

- 52 FAQ records
- 10 student-support categories
- NLP preprocessing
- TF-IDF vectorization
- Cosine similarity
- Confidence scoring
- Chat history
- Suggested questions
- Category filtering
- FAQ management
- Add FAQ
- Edit FAQ
- Delete FAQ
- Local CSV database
- Modern Streamlit UI

---

# Architecture

```mermaid
flowchart TD

A[User Query]
-->
B[Text Preprocessing]

B
-->
C[TF-IDF Vectorization]

C
-->
D[Cosine Similarity]

D
-->
E[Best FAQ Match]

E
-->
F[Confidence Evaluation]

F
-->
G{Confidence}

G -->|>= 70%| H[Confident Answer]

G -->|45-69%| I[Maybe Helpful Answer]

G -->|< 45%| J[Fallback Response]

H --> K[Chat UI]

I --> K

J --> K