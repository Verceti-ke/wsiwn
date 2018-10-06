import json
import os
from textwrap import dedent
from typing import Dict, List, Set, Tuple

import requests

OMDB_API_KEY = os.environ.get("OMDB_API_KEY")
OMDB_URL = "https://omdbapi.com"
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_media_info(movies: Set[str], tv: Set[str]) -> Tuple[List[Dict], List[Dict]]:
    """Get information about all movies and tv shows in the input sets"""
    data_movies: List[Dict] = []
    data_tv: List[Dict] = []
    fail: str = "\u274C"
    success: str = "\u2713"

    print("\n*** Fetching Movies ***")
    for m in movies:
        r = requests.get(
            OMDB_URL,
            params={"apikey": OMDB_API_KEY, "t": m, "type": "movie", "r": "json"},
        )
        res = r.json()
        if res["Response"] == "True":
            data_movies.append(res)
        print(f"{m} {success if res['Response'] == 'True' else fail}")
        r.close()

    print("\n*** Fetching TV Shows ***")
    for t in tv:
        r = requests.get(
            OMDB_URL,
            params={"apikey": OMDB_API_KEY, "t": t, "type": "series", "r": "json"},
        )
        res = r.json()
        if res["Response"] == "True":
            data_tv.append(res)
        print(f"{t} {success if res['Response'] == 'True' else fail}")
        r.close()

    return data_movies, data_tv


def write_prolog(movies: List[Dict], tv: List[Dict]) -> int:
    """Write Prolog statements for a fetched list of movies and tv shows"""
    count: int = 0
    dash: str = "\u2013"
    facts_movies: Set[str] = set()
    facts_tv: Set[str] = set()

    query_movie: str = dedent(
        """
        movie(X, Z) :-
            film(X),
            (   language(X, Z)
            ;   genre(X, Z)
            ;   duration(X, Z)
            ;   year(X, Z)
            ).

        movie(X, L, G, D, Y) :-
            film(X),
            language(X, L),
            genre(X, G),
            duration(X, D),
            year(X, Y).
    """
    )
    query_tv: str = dedent(
        """
        tv(X, Z) :-
            series(X),
            (   language(X, Z)
            ;   genre(X, Z)
            ;   duration(X, Z)
            ;   seasons(X, Z)
            ;   status(X, Z)
            ).

        tv(X, L, G, D, S, T) :-
            series(X),
            language(X, L),
            genre(X, G),
            duration(X, D),
            seasons(X, S),
            status(X, T).
    """
    )

    for m in movies:
        title = f"\"{m['Title']}\""
        try:
            runtime = int(m["Runtime"].split()[0]) / 60
        except ValueError as e:
            dur = "avg"
        else:
            if runtime <= 1.5:
                dur = "short"
            elif runtime >= 2.5:
                dur = "long"
            else:
                dur = "avg"

        q = dedent(
            f"""
            film({title}).
            language({title}, {m['Language'].split(',')[0].strip().lower()}).
            genre({title}, {m['Genre'].split(',')[0].strip().lower()}).
            duration({title}, {dur}).
            year({title}, {m['Year']}).
            """
        )
        facts_movies.add(q)
        count += 1

    for t in tv:
        title = f"\"{t['Title']}\""
        try:
            runtime = int(t["Runtime"].split()[0])
        except ValueError as e:
            dur = "avg"
        else:
            if runtime <= 30:
                dur = "short"
            elif runtime > 60:
                dur = "long"
            else:
                dur = "avg"

        q = dedent(
            f"""
            series({title}).
            language({title}, {t['Language'].split(',')[0].strip().lower()}).
            genre({title}, {t['Genre'].split(',')[0].strip().lower()}).
            duration({title}, {dur}).
            seasons({title}, {t['totalSeasons']}).
            status({title}, {'airing' if t['Year'].endswith(dash) else 'ended'}).
            """
        )
        facts_tv.add(q)
        count += 1

    with open(os.path.join(PROJECT_ROOT, "prolog/movies.pl"), "w") as fm:
        fm.write(":- style_check(- (discontiguous)).\n")
        for m in facts_movies:
            fm.write(m)
        fm.write(f"\n{query_movie}\n")

    with open(os.path.join(PROJECT_ROOT, "prolog/tv.pl"), "w") as ft:
        ft.write(":- style_check(- (discontiguous)).\n")
        for t in facts_tv:
            ft.write(t)
        ft.write(f"\n{query_tv}\n")

    return count


if __name__ == "__main__":
    movies = set()
    tv = set()

    with open(os.path.join(PROJECT_ROOT, "data/movies_list.txt"), "r") as fm:
        m = fm.readlines()
        movies = {x.strip() for x in m}

    with open(os.path.join(PROJECT_ROOT, "data/tv_list.txt"), "r") as ft:
        t = ft.readlines()
        tv = {x.strip() for x in t}

    data_movies, data_tv = get_media_info(movies, tv)
    m_json = {m["Title"]: m for m in data_movies}
    t_json = {t["Title"]: t for t in data_tv}

    with open(os.path.join(PROJECT_ROOT, "data/movies.json"), "w") as fm:
        json.dump(m_json, fm, indent=2, sort_keys=True)

    with open(os.path.join(PROJECT_ROOT, "data/tv.json"), "w") as ft:
        json.dump(t_json, ft, indent=2, sort_keys=True)

    count = write_prolog(data_movies, data_tv)
    print(f"\n{count} media entries written in Prolog knowledge base")
