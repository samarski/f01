"""Primjer rada web, flask, mysql"""
import configparser
from flask import Flask, request, render_template
import mysql.connector

config = configparser.ConfigParser()
config.read("config.ini")
dbconfig = config["database"]

app = Flask(__name__)

cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host = dbconfig["host"],
    user = dbconfig["user"],
    password = dbconfig["password"],
    database = dbconfig["database"],
    port = int(dbconfig["port"]),
    pool_name = "pool",
    pool_size = int(dbconfig["pool_size"])
)


@app.get("/test")
def get_test():
    """get test metoda"""
    return "Radi!!!"


@app.get("/json")
def get_json():
    """primjer get metode koja vraća json objekat"""
    return {
        "kurs": "Baze podataka",
        "Termin": "Ponedjeljak",
        "Studenti": [
            {
                "id": 1,
                "ime": "Student #1" 
            },
            { 
                "id": 2,
                "ime": "Student #2", 
            },
            {
                "id": 3,
                "ime": "Student #3"
            }
        ]
    }


@app.route("/lista_zaposlenika.html")
def get_lista_zaposlenika_html():
    """ Lista zaposlenika """

    lista_zaposlenika = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as z_cur:
            z_cur.execute(
                "select " + 
                "   z.zaposlenik_id, " + 
                "   z.ime, " + 
                "   z.prezime, " + 
                "   case when sz.zaposlenik_id is not null then 1 else 0 end as ima_sliku " +
                "from zaposlenik as z " + 
                "left outer join slika_zaposlenika as sz " +
                "on sz.zaposlenik_id = z.zaposlenik_id "  +
                "order by z.zaposlenik_id")

            lista_zaposlenika = z_cur.fetchall()

    return render_template("lista_zaposlenika.html", lista=lista_zaposlenika)


@app.get("/slika_zaposlenika")
def get_slika_zaposlenika():
    """ Lista zaposlenika preko named parametra"""
    args = request.args
    zaposlenik_id = args["zaposlenik_id"]

    cnx = cnxpool.get_connection()

    z_cur = cnx.cursor()

    z_cur.execute("select slika from slika_zaposlenika where zaposlenik_id = %s", (zaposlenik_id,))

    lista_zaposlenika = z_cur.fetchall()

    z_cur.close()

    cnx.close()

    if len(lista_zaposlenika) == 0:
        return ""

    return lista_zaposlenika[0][0]


@app.get("/slika_zaposlenika_v2/<int:zaposlenik_id>")
def get_slika_zaposlenika_v2(zaposlenik_id):
    """ Lista zaposlenika, ovaj put drugačije """

    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as z_cur:
            z_cur.execute("select slika " + 
                        "from slika_zaposlenika " + 
                        "where zaposlenik_id = %s", (zaposlenik_id,))

            lista_zaposlenika = z_cur.fetchall()

            if len(lista_zaposlenika) == 0:
                return ""

            return lista_zaposlenika[0][0]

    return ""


@app.post("/api/v2/zaposlenik")
def post_zaposlenik():
    """primjer post metode koja dodaje novog zaposlenika"""
    req_data = request.get_json()
    with cnxpool.get_connection() as db:
        with db.cursor() as stmt:
            try:
                stmt.execute("insert into zaposlenik " + 
                            "(ime, prezime, datum_rodjenja, mjesto_rodjenja) " + 
                            "values (%(ime)s, %(prezime)s, %(datum_rodjenja)s, %(mjesto_rodjenja)s)",
                            req_data)
                db.commit()

                return "Success", 201

            except Exception as e:
                return f"Error: {e}", 500


@app.get("/api/v2/zaposlenik")
def get_zaposlenik():
    """Primjer get metode koja vraća listu zaposlenika"""
    with cnxpool.get_connection() as db:
        z_cur = db.cursor()

        z_cur.execute("select * from zaposlenik order by zaposlenik_id")

        lista_zaposlenika = z_cur.fetchall()

        r = []
        for z in lista_zaposlenika:
            r.append(z)

        z_cur.close()

    return { "broj_slogova": z_cur.rowcount,
             "lista": r }
