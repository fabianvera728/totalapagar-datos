# ¿Cuánto cuesta sacar a Mbappé en sobres de EA FC 27?

- **Cuenta completa, con fuentes y transcripción:** https://totalapagar.com/videos/cuanto-cuesta-sacar-a-mbappe-en-sobres-fc-27/
- **Video:** https://www.youtube.com/watch?v=UjqbBW8jdqY
- **Datos consultados el:** 5 de octubre de 2026

## La pregunta

Si abres sobres de Ultimate Team hasta que te sale Kylian Mbappé (oro 91), ¿cuánto dinero gastas? EA publica la probabilidad mínima de cada categoría de carta, pero no la de cada jugador. Por eso la calculamos con un modelo y simulamos 10.000 jugadores.

## Resultados

Con el Large Gold Pack (150 FC Points) y el dinero al precio del paquete de 18.500 FC Points en Steam (USD 149,99):

| | Sobres | FC Points | USD |
|---|---|---|---|
| Probabilidad por sobre (modelo) | 1 de cada 2.670 | | |
| Mediana: a la mitad le costó más | 1.813 | 271.875 | 2.204 |
| Media | 2.655 | 398.216 | 3.229 |
| Percentil 90: a 1 de cada 10 le costó más | 6.142 | 921.300 | 7.470 |

La mediana equivale a 31 juegos completos de USD 69,99.

Con un presupuesto fijo, la probabilidad de sacarlo al menos una vez es:

| Gasto | Sobres | Probabilidad |
|---|---|---|
| USD 49,99 (5.900 FC Points) | 39 | 1,45 % |
| USD 99,99 (12.000 FC Points) | 80 | 2,95 % |
| USD 149,99 (18.500 FC Points) | 123 | 4,50 % |
| USD 749,95 (5 × 18.500 FC Points) | 616 | 20,6 % |

En la simulación de 10.000 sobres abiertos, 9.138 no traen ningún jugador de 84 o más, 862 sí, 50 traen uno de 90 o más y Mbappé sale 3 veces.

`resultados-simulacion-fc27.json` trae además el Full Swing Pack (400 FC Points), el caso de cualquiera de los tres jugadores 91 y los precios en EUR, MXN, COP y BRL.

## Supuestos

EA no publica la probabilidad de cada jugador, así que todo esto es un modelo nuestro:

1. **La probabilidad mínima publicada es la exacta.** EA muestra que un Large Gold Pack trae «como mínimo» un 8,8 % de probabilidad de un oro de 84 o más. La tomamos como el valor exacto.
2. **Como máximo un 84+ por sobre.** En el Large Gold Pack casi no cambia nada. En el Full Swing Pack, que trae 5 jugadores, subestima un poco.
3. **Todos los 84+ salen con la misma probabilidad.** Hay 235 jugadores de 84 o más, así que Mbappé sale en 0,088 / 235 de los sobres, 1 de cada 2.670. Este supuesto le favorece a EA: EA dice que la probabilidad de un jugador concreto es «significantly less» que la de su categoría. Por eso nuestras cifras son un piso: en la realidad, sacarlo cuesta más.
4. **Sin cartas especiales ni mercado.** No contamos Team of the Week, Icons, Heroes, variantes ni el mercado de transferencias. La pregunta es cuánto cuesta sacarlo en un sobre, no cuánto cuesta tenerlo.
5. **El dinero, al mejor precio por punto.** Usamos el paquete de 18.500 FC Points, el más barato por punto. Comprar paquetes más chicos cuesta más.

### Qué pasa si el supuesto 3 está mal

Si un 91 sale menos que un 84 promedio, el gasto crece en la misma proporción. Media teórica en USD:

| Si Mbappé sale… | 1 de cada… sobres | Media en USD |
|---|---|---|
| igual que un 84+ promedio | 2.670 | 3.248 |
| a la mitad de ese ritmo | 5.341 | 6.495 |
| a un cuarto | 10.682 | 12.991 |
| a un décimo | 26.705 | 32.476 |

### Qué pasa si cambia el 8,8 %

EA actualiza las probabilidades que muestra el juego. Entre septiembre y octubre de 2026, el «oro 84+» del Large Gold Pack apareció entre 8,6 % y 8,9 %. Con esos extremos, la mediana queda entre USD 2.179 y USD 2.255: sigue por encima de USD 2.000.

## Cómo reproducirla

Necesitas Python 3.10 o más reciente. No hace falta instalar nada.

```bash
python simulate_packs.py
```

La semilla está fija en 27, así que obtienes exactamente los mismos `resultados-simulacion-fc27.json` y `simulacion-sobres-fc27.csv`.

## Archivos

| Archivo | Qué es | Licencia |
|---|---|---|
| `simulate_packs.py` | El código de la simulación. Las fuentes de cada insumo están en su encabezado. | MIT |
| `simulacion-sobres-fc27.csv` | Los 10.000 jugadores simulados que abren Large Gold Packs hasta que les sale Mbappé, uno por fila. | CC BY 4.0 |
| `resultados-simulacion-fc27.json` | El resumen de todas las simulaciones: conteos, medianas, medias, percentiles, presupuestos y sensibilidad. | CC BY 4.0 |
| `ficha-de-cifras-fc27.csv` | Cada afirmación del video con el minuto en que aparece, la fuente, la URL y la fecha de consulta. | CC BY 4.0 |
| `precios-fc-points-steam.csv` | Los precios de los paquetes de FC Points en Steam en seis países. | CC BY 4.0 |
| `probabilidades-sobres-fc27.csv` | Las probabilidades mínimas por categoría que EA muestra para los dos sobres simulados, tal como las reproduce FUTMind. | CC BY 4.0 |
| `ratings-ea-fc27-top400.csv` | Los 400 jugadores mejor valorados de FC 27 según la base oficial de EA. | Datos de EA, no están bajo nuestra licencia |

### Columnas de `simulacion-sobres-fc27.csv`

| Columna | Qué es |
|---|---|
| `jugador` | Número del jugador simulado, de 1 a 10.000 |
| `sobres` | Sobres que abrió hasta que le salió Mbappé |
| `fc_points` | `sobres` × 150 |
| `usd`, `eur`, `mxn`, `cop`, `brl` | Lo que cuestan esos FC Points al precio por punto del paquete de 18.500 en Steam de Estados Unidos, España, México, Colombia y Brasil |

## Fuentes de los insumos

- **Probabilidades:** pantalla «Show Pack Probabilities» de EA, reproducida por FUTMind. [Large Gold Pack](https://futmind.com/pack/301/large-gold-pack), vigente desde el 17-sep-2026. [Full Swing Pack](https://futmind.com/pack/20200/full-swing-pack), vigente desde el 2-oct-2026.
- **Cómo leer esas probabilidades:** EA, [Ultimate Team Probabilities in EA SPORTS FC](https://www.ea.com/games/ea-sports-fc/news/fc-pack-probabilities), 20-ago-2026.
- **Jugadores de 84 o más:** EA, [ratings de FC 27](https://www.ea.com/games/ea-sports-fc/ratings), páginas 1 a 4.
- **Precios:** Steam, [EA SPORTS FC 27 - FC Points](https://store.steampowered.com/api/appdetails?appids=4314910&cc=US) (cambia `cc` por ES, MX, CO, BR o GB) y [EA SPORTS FC 27](https://store.steampowered.com/app/4080220/).

Total a Pagar es un canal independiente. No tiene relación con EA ni con la FIFA, ni está patrocinado por ellas.
