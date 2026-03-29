"""
Reddit scraper utility for the DEADPOOL Product Agent.

Fetches posts and comments from a subreddit via Reddit's public JSON API.
No API key required — uses the public .json endpoint.
"""
from __future__ import annotations

import logging
import random
import time
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("deadpool.reddit_scraper")

USER_AGENT = "Mozilla/5.0 (compatible; DEADPOOLRiskMonitor/1.0; educational project)"


def _make_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        follow_redirects=True,
        timeout=30.0,
    )


def _scrape_feed(subreddit: str, max_pages: int) -> list[dict]:
    """Fetch posts from the subreddit listing."""
    all_posts: list[dict] = []
    after = None
    base_url = f"https://www.reddit.com/r/{subreddit}.json"

    for page_num in range(1, max_pages + 1):
        params: dict[str, Any] = {"limit": 100, "raw_json": 1}
        if after:
            params["after"] = after

        try:
            with _make_client() as client:
                resp = client.get(base_url, params=params)
            if resp.status_code != 200:
                logger.warning("Reddit feed returned HTTP %s on page %d", resp.status_code, page_num)
                break
            data = resp.json()
        except Exception as exc:
            logger.warning("Reddit feed fetch failed on page %d: %s", page_num, exc)
            break

        listing = data.get("data", {})
        children = listing.get("children", [])
        if not children:
            break

        for child in children:
            post = child.get("data", {})
            all_posts.append({
                "title": post.get("title", ""),
                "author": post.get("author", "[deleted]"),
                "score": post.get("score", 0),
                "comment_count": post.get("num_comments", 0),
                "post_url": f"https://www.reddit.com{post.get('permalink', '')}",
                "flair": post.get("link_flair_text") or "",
                "post_id": post.get("name", ""),
                "selftext": post.get("selftext", ""),
                "created_utc": post.get("created_utc", 0),
                "comments": [],
            })

        after = listing.get("after")
        if not after:
            break

        time.sleep(random.uniform(1.0, 2.0))

    return all_posts


def _scrape_comments(post_url: str) -> list[dict]:
    """Fetch comments for a single post."""
    json_url = post_url.rstrip("/") + ".json"
    params = {"limit": 200, "depth": 5, "raw_json": 1}

    try:
        with _make_client() as client:
            resp = client.get(json_url, params=params)
        if resp.status_code != 200:
            return []
        data = resp.json()
    except Exception as exc:
        logger.warning("Reddit comment fetch failed for %s: %s", post_url, exc)
        return []

    if not isinstance(data, list) or len(data) < 2:
        return []

    comment_listing = data[1].get("data", {}).get("children", [])

    def extract(children: list, depth: int = 0) -> list[dict]:
        results = []
        for child in children:
            if child.get("kind") != "t1":
                continue
            cdata = child.get("data", {})
            results.append({
                "author": cdata.get("author", "[deleted]"),
                "score": cdata.get("score", 0),
                "depth": cdata.get("depth", depth),
                "body": cdata.get("body", ""),
            })
            replies = cdata.get("replies")
            if isinstance(replies, dict):
                results.extend(extract(replies.get("data", {}).get("children", []), depth + 1))
        return results

    return extract(comment_listing)


def fetch_subreddit_data(
    subreddit: str,
    max_pages: int = 3,
    fetch_comments: bool = True,
) -> dict:
    """
    Fetch posts (and optionally comments) from a subreddit.

    Returns a dict with:
      - subreddit: str
      - scraped_at: ISO timestamp
      - post_count: int
      - posts: list of post dicts, each with a 'comments' list
    """
    logger.info("Fetching r/%s (max_pages=%d, comments=%s)", subreddit, max_pages, fetch_comments)
    posts = _scrape_feed(subreddit, max_pages)
    logger.info("Fetched %d posts from r/%s", len(posts), subreddit)

    if fetch_comments:
        for post in posts:
            if post["post_url"]:
                post["comments"] = _scrape_comments(post["post_url"])
                time.sleep(random.uniform(0.5, 1.0))

    return {
        "subreddit": subreddit,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "post_count": len(posts),
        "posts": posts,
    }
