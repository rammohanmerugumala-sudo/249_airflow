import requests, pandas as pd, pathlib

BASE = "https://jsonplaceholder.typicode.com"
RAW = pathlib.Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)
PROC = pathlib.Path("data/processed"); PROC.mkdir(parents=True, exist_ok=True)

def fetch(endpoint: str):
    r = requests.get(f"{BASE}/{endpoint}", timeout=10)
    r.raise_for_status()
    return r.json()

def ingest():
    users = pd.json_normalize(fetch("users"))
    posts = pd.json_normalize(fetch("posts"))
    return users, posts

def transform(users: pd.DataFrame, posts: pd.DataFrame):
    # sanity
    assert users["id"].notna().all(), "users.id has nulls"
    assert posts["id"].notna().all(), "posts.id has nulls"

    # enrich posts with author info
    cols_user = ["id", "name", "email"]
    enriched = posts.merge(users[cols_user], left_on="userId", right_on="id", how="left", suffixes=("", "_user"))
    enriched.rename(columns={"id_user": "user_id"}, inplace=True)

    # posts per user
    ppu = enriched.groupby(["userId", "name"], as_index=False).size().rename(columns={"size": "posts_count"})

    # top author by post count
    top = ppu.sort_values("posts_count", ascending=False).head(1)

    return enriched, ppu, top

def load(enriched: pd.DataFrame, ppu: pd.DataFrame, top: pd.DataFrame):
    enriched.to_csv(PROC / "posts_enriched.csv", index=False)
    ppu.to_csv(PROC / "posts_per_user.csv", index=False)
    top.to_csv(PROC / "top_author.csv", index=False)

def run():
    users, posts = ingest()
    enriched, ppu, top = transform(users, posts)
    load(enriched, ppu, top)
    print(f"Done. rows: posts={len(posts)}, users={len(users)}")

if __name__ == "__main__":
    run()