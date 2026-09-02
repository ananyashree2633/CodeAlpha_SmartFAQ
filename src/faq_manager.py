"""
FAQ CRUD management using CSV.
"""

from pathlib import Path

import pandas as pd


COLUMNS = [
    "question",
    "answer",
    "category"
]

# LOAD FAQS


def load_faqs(csv_path):

    path = Path(csv_path)

    if not path.exists():

        return pd.DataFrame(
            columns=COLUMNS
        )

    df = pd.read_csv(path)

    for column in COLUMNS:

        if column not in df.columns:
            df[column] = ""

    return df[
        COLUMNS
    ].fillna("")

# SAVE FAQS


def save_faqs(df, csv_path):

    path = Path(csv_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df[
        COLUMNS
    ].to_csv(
        path,
        index=False
    )

# ADD FAQ

def add_faq(
    csv_path,
    question,
    answer,
    category
):

    df = load_faqs(csv_path)

    new_row = pd.DataFrame([
        {
            "question": question.strip(),
            "answer": answer.strip(),
            "category": category.strip()
        }
    ])

    df = pd.concat(
        [
            df,
            new_row
        ],
        ignore_index=True
    )

    save_faqs(
        df,
        csv_path
    )

# UPDATE FAQ

def update_faq(
    csv_path,
    index,
    question,
    answer,
    category
):

    df = load_faqs(csv_path)

    if index < 0 or index >= len(df):

        raise IndexError(
            "FAQ index is out of range."
        )

    df.loc[
        index,
        COLUMNS
    ] = [
        question.strip(),
        answer.strip(),
        category.strip()
    ]

    save_faqs(
        df,
        csv_path
    )


# DELETE FAQ


def delete_faq(
    csv_path,
    index
):

    df = load_faqs(csv_path)

    if index < 0 or index >= len(df):

        raise IndexError(
            "FAQ index is out of range."
        )

    df = df.drop(
        index=index
    )

    df = df.reset_index(
        drop=True
    )

    save_faqs(
        df,
        csv_path
    )