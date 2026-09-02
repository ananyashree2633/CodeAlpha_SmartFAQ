"""
NLP chatbot engine
using 
NLTK for preprocessing
TF-IDF vectorisation
cosine similarity
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import preprocess_text

class engine:
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1,2),
            sublinear_tf=True,
            min_df=1
        )

        self.faqs = pd.DataFrame()
        self.matrix = None
        self.reload()

    #load

    def reload(self):
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"FAQ dataset not found: {self.csv_path}"
            )    

        try:
            df = pd.read_csv(self.csv_path)

        except Exception as error:
            raise ValueError(
                f"Invalid FAQ CSV file: {error}"
            )    
        required_columns = {
            "question",
            "answer",
            "category"
        }

        if not required_columns.issubset(df.columns):
            raise ValueError(
                "CSV must contain: "
                "question, answer and category columns."
            )

        #remove missing data
        df = df.dropna(
            subset=[
                "question",
                "answer",
                "category"
            ]
        ).copy()

        #convert to strings
        df["question"] = df["question"].astype(str).str.strip()
        df["answer"] = df["answer"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip()

        #remove empty records
        df = df[
            (df["question"] != "") &
            (df["answer"] != "") &
            (df["category"] != "")
        ]
        if df.empty:
            raise ValueError(
                "FAQdata set is empty."
            )
        # NLP preprocessing

        df["processed_question"] = (

            df["question"]

            .apply(preprocess_text)

        )

        self.faqs = df.reset_index(drop=True)

        if self.faqs[

            "processed_question"

        ].str.strip().eq("").all():

            raise ValueError(

                "FAQ questions could not be processed."

            )

        # TF-IDF

        self.matrix = self.vectorizer.fit_transform(

            self.faqs["processed_question"]

        )
        #confidence label
        @staticmethod

        def confidence_label(score):
            if score >= 0.70:
                return "Confident answer"

            elif score >= 0.45:
                return "I think this may help"

            return "Low confidence"

    #ask question
    def ask(self, query, category="All"):

        query = (query or "").strip()

        # Empty question

        if not query:

            return {

                "answer": (

                    "Please enter a question "

                    "so I can help."

                ),

                "confidence": 0.0,

                "category": "General",

                "matched_question": "No question entered",

                "status": "empty"

            }

        # Very short question

        if len(query.split()) < 2:

            return {

                "answer": (

                    "Please enter a little more detail. "

                    "For example: "

                    "\"What is the minimum attendance requirement?\""

                ),

                "confidence": 0.0,

                "category": "General",

                "matched_question": "Question too short",

                "status": "short"

            }

        # Preprocess user query

        processed_query = preprocess_text(query)

        if not processed_query:

            return {

                "answer": (

                    "I could not extract meaningful words "

                    "from that question. Please try again."

                ),

                "confidence": 0.0,

                "category": "General",

                "matched_question": "No meaningful terms",

                "status": "invalid"

            }

        # Convert query into TF-IDF vector

        query_vector = self.vectorizer.transform(

            [processed_query]

        )

        # Calculate cosine similarity

        scores = cosine_similarity(

            query_vector,

            self.matrix

        ).flatten()

        # Category filtering

        if category != "All":

            allowed = (

                self.faqs["category"]

                .eq(category)

                .to_numpy()

            )

            scores = np.where(

                allowed,

                scores,

                -1.0

            )

        # Best match

        best_index = int(

            np.argmax(scores)

        )

        best_score = max(

            float(scores[best_index]),

            0.0

        )

        # FALLBACK

        if best_score < 0.45:

            return {

                "answer": (

                    "I'm not confident I understood "

                    "that question. Try asking about "

                    "admissions, fees, exams, scholarships, "

                    "placements, hostel, attendance, "

                    "or library."

                ),

                "confidence": best_score,

                "category": "General",

                "matched_question": (

                    self.faqs.iloc[best_index]["question"]

                ),

                "status": "fallback"

            }

        # Best FAQ

        row = self.faqs.iloc[best_index]

        # Medium confidence

        prefix = ""

        if best_score < 0.70:

            prefix = "I think this may help: "

        return {

            "answer": prefix + row["answer"],

            "confidence": best_score,

            "category": row["category"],

            "matched_question": row["question"],

            "status": "matched"

        }

    # STATISTICS

    def stats(

        self,

        answered_count=0,

        avg_confidence=0.0

    ):

        return {

            "total_faqs":

                len(self.faqs),

            "categories":

                int(

                    self.faqs[

                        "category"

                    ].nunique()

                ),

            "questions_answered":

                answered_count,

            "avg_confidence":

                avg_confidence

        }


    # CATEGORIES


    def categories(self):

        return sorted(

            self.faqs[

                "category"

            ].unique().tolist()

        )
