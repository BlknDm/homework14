import sqlite3
from flask import Flask
import json

app = Flask(__name__)


def get_data_by_sql(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row

        result = connection.execute(sql).fetchall()

    return result


@app.get("/movie/<title>/")
def search_by_title(title):
    result = []
    for item in get_data_by_sql(sql=f"""
            SELECT `title`, `country`, `release_year`, `listed_in` as `genre`, `description`
            FROM netflix
            WHERE title = '{title}'
            ORDER BY release_year DESC
            LIMIT 1
            """):
        result = dict(item)

    return app.response_class(json.dumps(result, ensure_ascii=False, indent=4), mimetype="application/json", status=200)


@app.get("/movie/<int:year1>/to/<int:year2>/")
def search_by_year(year1, year2):
    sql = f"""
            SELECT * FROM netflix
            WHERE release_year BETWEEN {year1} AND {year2}
            LIMIT 100
            """
    result = []

    for item in get_data_by_sql(sql):
        result.append(dict(item))

    return app.response_class(json.dumps(result, ensure_ascii=False, indent=4), mimetype="application/json", status=200)


@app.get("/rating/<rating>/")
def search_by_rating(rating):
    my_rating = {
        "children": ('G', 'G'),
        "family": ('G', 'PG', 'PG-13'),
        "adult": ('R', 'NC-17')
    }

    sql = f"""
            SELECT * FROM netflix
            WHERE rating in {my_rating.get(rating, ('PG', 'NC-17'))}
            """

    result = []

    for item in get_data_by_sql(sql):
        result.append(dict(item))

    return app.response_class(json.dumps(result, ensure_ascii=False, indent=4), mimetype="application/json", status=200)


@app.get("/genre/<genre>/")
def search_by_genre(genre):
    sql = f"""
            SELECT show_id, type FROM netflix
            WHERE listed_in LIKE '%{str(genre).title()}%'
            """

    result = []

    for item in get_data_by_sql(sql):
        result.append(dict(item))

    return app.response_class(json.dumps(result, ensure_ascii=False, indent=4), mimetype="application/json", status=200)


def search_by_actor(name1, name2):
    sql = f'''
            SELECT title, `cast` FROM netflix
            where "cast" LIKE '%{name1}%' AND "cast" LIKE '%{name2}%'
            '''
    names_dict = {}

    for item in get_data_by_sql(sql):
        result = dict(item)

        names = set(result.get('cast').split(", ")) - {name1, name2}

        for name in names:
            names_dict[name.strip()] = names_dict.get(name.strip(), 0) + 1

    for key, value in names_dict.items():
        if value > 2:
            print(key)

    return json.dumps(names_dict, ensure_ascii=False, indent=4)


#print(search_by_actor('Rose McIver', 'Ben Lamb'))


def global_search(types, year, genre):
    sql = f'''
              SELECT * FROM netflix
              where type = '{types.title()}' AND release_year = '{year}' AND listed_in LIKE '%{genre.title()}%'
            '''

    result = []

    for item in get_data_by_sql(sql):
        result.append(dict(item))

    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app.run(host="localhost", port=4542)
