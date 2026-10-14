import faiss
import numpy as np
from sqlalchemy.orm import Session
from app.models.submission import Submission

DIMENSION = 384

# IndexIDMap2 accurately maps custom SQLite IDs to FAISS vectors
vector_index = faiss.IndexIDMap2(faiss.IndexFlatIP(DIMENSION))

def build_faiss_index(db: Session):
    """Rebuilds the ephemeral FAISS index from the SQLite database source of truth."""
    print("Rebuilding FAISS vector index from SQLite...")

    submissions = db.query(Submission).filter(Submission.embedding.is_not(None)).all()

    if not submissions:
        print("No existing embeddings found. FAISS index initialized empty.")
        return

    vectors = []
    ids = []

    for sub in submissions:
        vectors.append(sub.embedding)
        ids.append(sub.id)

    vectors_np = np.array(vectors, dtype=np.float32)
    ids_np = np.array(ids, dtype=np.int64)

    vector_index.reset()
    vector_index.add_with_ids(vectors_np, ids_np)

    print(f"✅ Successfully loaded {vector_index.ntotal} vectors into FAISS.")

def add_single_vector_to_index(submission_id: int, embedding: list[float]):
    """Adds a newly created submission to the live FAISS index immediately."""
    vector_np = np.array([embedding], dtype=np.float32)
    id_np = np.array([submission_id], dtype=np.int64)
    vector_index.add_with_ids(vector_np, id_np)

def search_similar_submissions(embedding: list[float], threshold: float = 0.85):
    """
    Searches FAISS for existing submissions.
    Returns the mapped SQLite ID of the closest match if it exceeds the threshold.
    """
    if vector_index.ntotal == 0:
        return None

    query_vector = np.array([embedding], dtype=np.float32)

    D, I = vector_index.search(query_vector, k=1)

    best_score = D[0][0]
    best_id = I[0][0]

    print(f"DEBUG: Top match score is {best_score} for ID {best_id}")

    if best_score >= threshold:
        return int(best_id)

    return None