"""
Microsimulación de sobres de EA SPORTS FC 27 Ultimate Team.
Cuenta: https://totalapagar.com/videos/cuanto-cuesta-sacar-a-mbappe-en-sobres-fc-27/  ·  2026-10-05

Qué calcula
-----------
1. Abre 10.000 sobres "Large Gold Pack" (150 FC Points) y cuenta qué sale por categoría.
2. Simula 10.000 jugadores que abren sobres hasta sacar a Kylian Mbappé (carta base oro, 91 OVR)
   y reporta media, mediana, percentil 90 y 99 de sobres, FC Points y dinero real.
3. Repite el punto 2 con un sobre más caro ("Full Swing Pack", 400 FC Points, 5 jugadores).
4. Calcula la probabilidad de sacar a Mbappé con presupuestos concretos (precio del juego, 12.000 FC Points).

Fuentes de los insumos (todas consultadas el 2026-10-05)
-------------------------------------------------------
[P1] Probabilidades por categoría de cada sobre: pantalla "Show Pack Probabilities" de EA, tal como
     la captura FUTMind en su lista de sobres de FC 27 (campo `odds`, con timestamp de EA).
     https://futmind.com/pack/301/large-gold-pack  ->  resumen: probabilidades-sobres-fc27.csv
     · Large Gold Pack (id 301, 12 ítems, 150 FC Points / 7.500 monedas, timestamp 2026-09-17):
       Oro 75+ 100 % · Oro 82+ 55 % · Oro 84+ 8,8 % · Team of the Week 1,0 %
     · Full Swing Pack (id 20200, 5 jugadores, 400 FC Points / 25.000 monedas, timestamp 2026-10-02):
       Oro 75+ 100 % · Oro 82+ 99 % · Oro 84+ 64 % · TOTW/Hero/Icon/DFG <1 %
     EA explica el significado de esas cifras en https://www.ea.com/games/ea-sports-fc/news/fc-pack-probabilities
     (2026-08-20): son la probabilidad MÍNIMA de recibir uno o más ítems de la categoría; "the probability of
     receiving a particular individual item is significantly less [...] and is often less than 1%".
[P2] Cuántos jugadores hay con 84+ OVR en FC 27: base oficial de ratings de EA, páginas 1-4 de
     https://www.ea.com/games/ea-sports-fc/ratings  ->  copia: ratings-ea-fc27-top400.csv
     Recuento: 91:3 · 90:11 · 89:13 · 88:18 · 87:28 · 86:30 · 85:61 · 84:71  =>  235 jugadores 84+.
     Mbappé = 91 (rank 1). Los otros 91: Alexia Putellas y Erling Haaland.
[P3] Precio de los FC Points: tienda de Steam, app 4314910 "EA SPORTS FC 27 - FC Points"
     (https://store.steampowered.com/api/appdetails?appids=4314910&cc=XX). Ver PRICES abajo
     y precios-fc-points-steam.csv.

Suposiciones (EA NO publica la probabilidad por jugador; todo lo que sigue es modelo nuestro)
------------------------------------------------------------------------------------------
S1. Se toma la probabilidad mínima publicada como probabilidad exacta de "al menos un 84+".
S2. Un sobre trae como máximo UNA carta 84+ (en el Full Swing Pack, de 5 jugadores, puede haber más:
    esto subestima un poco el número de 84+ por sobre).
S3. Dado que sale un 84+, es cualquiera de los 235 jugadores 84+ con la MISMA probabilidad (uniforme).
    Es una suposición OPTIMISTA para cartas top: EA dice que la probabilidad individual es "significantly
    less" y los datos comunitarios muestran que los 84 salen mucho más que los 90+. Por eso el costo real
    de un 91 probablemente es MAYOR que el calculado aquí. Se incluye un análisis de sensibilidad.
S4. Se ignoran cartas especiales (TOTW, Icon, Hero, holográficas) y el mercado de transferencias:
    la pregunta es "¿cuánto cuesta sacarlo en un sobre?", no "¿cuánto cuesta tenerlo?".
S5. El dinero se calcula al precio por punto del paquete más grande (18.500 FC Points), que es el más
    barato por punto: es un piso. También se informa con el de 12.000.

Uso:  python simulate_packs.py      (Python 3.10+, solo biblioteca estándar; semilla fija = 27)
Salida, en esta carpeta:
  resultados-simulacion-fc27.json   resumen de todas las simulaciones
  simulacion-sobres-fc27.csv        los 10.000 jugadores de la simulación 2, uno por fila
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

SEED = 27
N_PACKS = 10_000      # sobres abiertos en la simulación 1
N_PLAYERS = 10_000    # jugadores simulados en la simulación 2 y 3

HERE = Path(__file__).resolve().parent

# [P1] Probabilidades por categoría publicadas por EA (pantalla del juego, vía FUTMind)
PACKS = {
    "large_gold": {
        "name": "Large Gold Pack",
        "futmind_id": 301,
        "fc_points": 150,
        "coins": 7_500,
        "items": 12,
        "p_82plus": 0.55,
        "p_84plus": 0.088,
        "p_totw": 0.010,
        "ea_timestamp": "2026-09-17",
    },
    "full_swing": {
        "name": "Full Swing Pack",
        "futmind_id": 20200,
        "fc_points": 400,
        "coins": 25_000,
        "items": 5,
        "p_82plus": 0.99,
        "p_84plus": 0.64,
        "p_totw": None,  # publicado como "<1%"
        "ea_timestamp": "2026-10-02",
    },
}

# [P3] Precios de FC Points en Steam (2026-10-05). {moneda: {puntos: precio}}
PRICES = {
    "USD": {500: 4.99, 1050: 9.99, 1600: 14.99, 2800: 24.99, 5900: 49.99, 12000: 99.99, 18500: 149.99},
    "EUR": {500: 4.99, 1050: 9.99, 1600: 14.99, 2800: 24.99, 5900: 49.99, 12000: 99.99, 18500: 149.99},
    "MXN": {500: 109.0, 1050: 199.0, 1600: 299.0, 2800: 499.0, 5900: 999.0, 12000: 1999.0, 18500: 2999.0},
    "COP": {500: 20999, 1050: 41999, 1600: 61999, 2800: 103999, 5900: 206999, 12000: 413999, 18500: 619999},
    "BRL": {500: 27.90, 1050: 54.90, 1600: 80.90, 2800: 134.90, 5900: 269.90, 12000: 534.90, 18500: 799.90},
}
GAME_PRICE_USD = 69.99  # EA SPORTS FC 27 estándar en Steam (app 4080220), 2026-10-05


def load_pool() -> tuple[list[tuple[str, int]], Counter]:
    """[P2] Jugadores 84+ de la base de ratings de EA (copia local)."""
    pool = []
    with open(HERE / "ratings-ea-fc27-top400.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            ovr = int(row["ovr"])
            if ovr >= 84:
                pool.append((f"{row['first_name']} {row['last_name']}".strip(), ovr))
    return pool, Counter(o for _, o in pool)


def pct(values: list[int], q: float) -> float:
    """Percentil por el método del rango más cercano (simple y reproducible)."""
    s = sorted(values)
    k = max(0, math.ceil(q / 100 * len(s)) - 1)
    return s[k]


def per_point(currency: str, bundle: int) -> float:
    return PRICES[currency][bundle] / bundle


def money(fc_points: float) -> dict:
    out = {}
    for cur in PRICES:
        out[cur] = {
            "al_precio_del_paquete_18500": round(fc_points * per_point(cur, 18500), 2),
            "al_precio_del_paquete_12000": round(fc_points * per_point(cur, 12000), 2),
        }
    return out


def geometric(rng: random.Random, p: float) -> int:
    """Número de sobres hasta el primer éxito (inversa exacta de la geométrica)."""
    u = rng.random()
    return max(1, math.ceil(math.log(1.0 - u) / math.log(1.0 - p)))


def open_packs(rng: random.Random, pack: dict, pool: list[tuple[str, int]], target: str) -> dict:
    """Simulación 1: abrir N_PACKS sobres y contar resultados."""
    c = Counter()
    by_rating = Counter()
    for _ in range(N_PACKS):
        c["sobres"] += 1
        if rng.random() < pack["p_82plus"]:
            c["con_82_o_mas"] += 1
        if pack["p_totw"] and rng.random() < pack["p_totw"]:
            c["con_TOTW"] += 1
        if rng.random() < pack["p_84plus"]:
            c["con_84_o_mas"] += 1
            name, ovr = rng.choice(pool)
            by_rating[ovr] += 1
            if ovr >= 90:
                c["con_90_o_mas"] += 1
            if ovr == 91:
                c["con_un_91"] += 1
            if name == target:
                c["con_" + target.replace(" ", "_")] += 1
    c["sin_nada_84_o_mas"] = c["sobres"] - c["con_84_o_mas"]
    return {"conteos": dict(c), "84plus_por_rating": dict(sorted(by_rating.items(), reverse=True))}


def chase(rng: random.Random, pack: dict, p_target: float, label: str) -> tuple[dict, list[int]]:
    """Simulación 2/3: N_PLAYERS jugadores abren sobres hasta sacar la carta objetivo."""
    packs = [geometric(rng, p_target) for _ in range(N_PLAYERS)]
    fp = [n * pack["fc_points"] for n in packs]
    summary = {
        "objetivo": label,
        "sobre": pack["name"],
        "fc_points_por_sobre": pack["fc_points"],
        "p_por_sobre": p_target,
        "uno_en_N_sobres": round(1 / p_target),
        "teorico_media_sobres": round(1 / p_target, 1),
        "teorico_mediana_sobres": math.ceil(math.log(0.5) / math.log(1 - p_target)),
        "sim_media_sobres": round(statistics.mean(packs), 1),
        "sim_mediana_sobres": statistics.median(packs),
        "sim_p90_sobres": pct(packs, 90),
        "sim_p99_sobres": pct(packs, 99),
        "sim_min_sobres": min(packs),
        "sim_max_sobres": max(packs),
        "pct_jugadores_que_lo_sacan_en_10_sobres_o_menos": round(100 * sum(n <= 10 for n in packs) / N_PLAYERS, 2),
    }
    for key, val in (("media", statistics.mean(fp)), ("mediana", statistics.median(fp)),
                     ("p90", pct(fp, 90)), ("p99", pct(fp, 99))):
        summary[f"fc_points_{key}"] = round(val)
        summary[f"dinero_{key}"] = money(val)
    return summary, packs


def write_players(path: Path, pack: dict, packs: list[int]) -> None:
    """Un jugador simulado por fila: sobres hasta sacar la carta, FC Points y dinero al mejor precio por punto."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        out = csv.writer(fh)
        out.writerow(["jugador", "sobres", "fc_points", "usd", "eur", "mxn", "cop", "brl"])
        for player, n in enumerate(packs, start=1):
            fp = n * pack["fc_points"]
            out.writerow([player, n, fp, *(round(fp * per_point(cur, 18500), 2) for cur in ("USD", "EUR", "MXN", "COP", "BRL"))])


def budget_odds(pack: dict, p_target: float) -> list[dict]:
    """Probabilidad de sacar la carta con presupuestos concretos (analítico)."""
    out = []
    for label, fp in (("5.900 FC Points (USD/EUR 49,99)", 5900),
                      ("12.000 FC Points (USD/EUR 99,99)", 12000),
                      ("18.500 FC Points (USD/EUR 149,99)", 18500),
                      ("5 x 18.500 FC Points (USD/EUR 749,95)", 92500)):
        n = fp // pack["fc_points"]
        out.append({"presupuesto": label, "fc_points": fp, "sobres": n,
                    "p_de_sacarlo_pct": round(100 * (1 - (1 - p_target) ** n), 2)})
    return out


def main() -> None:
    rng = random.Random(SEED)
    pool, counts = load_pool()
    target = "Kylian Mbappé"
    assert (target, 91) in pool, "Mbappé 91 no está en la copia de ratings"
    n91 = counts[91]
    n_pool = len(pool)

    results = {
        "meta": {
            "fecha": "2026-10-05",
            "semilla": SEED,
            "n_sobres_sim1": N_PACKS,
            "n_jugadores_sim2": N_PLAYERS,
            "pool_84plus": n_pool,
            "pool_por_rating": dict(sorted(counts.items(), reverse=True)),
            "suposiciones": ["S1 prob. mínima = exacta", "S2 máx. un 84+ por sobre",
                             "S3 uniforme entre los 84+ (optimista para cartas top)",
                             "S4 sin cartas especiales ni mercado", "S5 dinero al mejor precio por punto"],
        },
        "sim1_abrir_10000_large_gold": open_packs(rng, PACKS["large_gold"], pool, target),
        "sim2_perseguir_mbappe_large_gold": None,
        "sim3_perseguir_mbappe_full_swing": None,
        "sim4_cualquier_91_large_gold": None,
        "presupuestos_large_gold": None,
        "presupuestos_full_swing": None,
        "sensibilidad": [],
    }

    for key, pk in (("sim2_perseguir_mbappe_large_gold", "large_gold"),
                    ("sim3_perseguir_mbappe_full_swing", "full_swing")):
        p = PACKS[pk]["p_84plus"] / n_pool
        results[key], packs = chase(rng, PACKS[pk], p, f"{target} (oro base 91)")
        if pk == "large_gold":
            write_players(HERE / "simulacion-sobres-fc27.csv", PACKS[pk], packs)

    p_any91 = PACKS["large_gold"]["p_84plus"] * n91 / n_pool
    results["sim4_cualquier_91_large_gold"], _ = chase(rng, PACKS["large_gold"], p_any91,
                                                       "cualquiera de los 3 jugadores 91")

    results["presupuestos_large_gold"] = budget_odds(PACKS["large_gold"], PACKS["large_gold"]["p_84plus"] / n_pool)
    results["presupuestos_full_swing"] = budget_odds(PACKS["full_swing"], PACKS["full_swing"]["p_84plus"] / n_pool)

    # Sensibilidad a S3: si un 91 sale la mitad, un cuarto o una décima parte de lo que sale un 84+ "promedio".
    for factor in (1.0, 0.5, 0.25, 0.1):
        p = PACKS["large_gold"]["p_84plus"] / n_pool * factor
        mean_fp = PACKS["large_gold"]["fc_points"] / p
        results["sensibilidad"].append({
            "peso_relativo_de_un_91": factor,
            "uno_en_N_large_gold": round(1 / p),
            "fc_points_media": round(mean_fp),
            "usd_media_paquete_18500": round(mean_fp * per_point("USD", 18500), 2),
        })

    results["referencia"] = {
        "precio_juego_usd": GAME_PRICE_USD,
        "usd_por_fc_point_18500": round(per_point("USD", 18500), 6),
        "usd_por_fc_point_12000": round(per_point("USD", 12000), 6),
    }

    out = HERE / "resultados-simulacion-fc27.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    s1 = results["sim1_abrir_10000_large_gold"]["conteos"]
    s2 = results["sim2_perseguir_mbappe_large_gold"]
    s3 = results["sim3_perseguir_mbappe_full_swing"]
    print(f"Pool 84+: {n_pool} jugadores ({dict(sorted(counts.items(), reverse=True))})")
    print(f"Sim1 10.000 Large Gold: {s1}")
    for s in (s2, s3, results["sim4_cualquier_91_large_gold"]):
        print(f"{s['objetivo']} · {s['sobre']}: 1 en {s['uno_en_N_sobres']} · mediana {s['sim_mediana_sobres']} "
              f"sobres · p90 {s['sim_p90_sobres']} · USD mediana {s['dinero_mediana']['USD']['al_precio_del_paquete_18500']} "
              f"· USD media {s['dinero_media']['USD']['al_precio_del_paquete_18500']} "
              f"· USD p90 {s['dinero_p90']['USD']['al_precio_del_paquete_18500']}")
    print("Presupuestos Large Gold:", results["presupuestos_large_gold"])
    print("Presupuestos Full Swing:", results["presupuestos_full_swing"])
    print("Sensibilidad:", results["sensibilidad"])
    print(f"-> {out}")


if __name__ == "__main__":
    main()
