# Calculadora de Series de Taylor y Maclaurin

Aplicación web interactiva contenida en un solo archivo de Python. Permite calcular y visualizar la aproximación de funciones mediante series de Taylor y Maclaurin.

## Características

* **Entrada dinámica:** Permite definir la función, el centro de la serie (a), el punto de evaluación (x), el número de términos y la tolerancia objetivo.
* **Modo Maclaurin:** Opción para forzar el centro de la serie a 0.
* **Tabla de iteraciones:** Muestra el cálculo paso a paso, incluyendo la derivada, el término actual, la sumatoria acumulada, el error absoluto y el error relativo.
* **Visualización gráfica:** Genera cuatro gráficas interactivas (iteración vs términos, iteración vs sumatoria, iteración vs errores y convergencia vs tolerancia).
* **Métricas adicionales:** Calcula la tasa de convergencia y el número de términos necesarios para alcanzar la tolerancia definida.
* **Exportación:** Permite descargar la tabla de resultados en formato CSV.
* **Validación:** Incluye manejo de excepciones para sintaxis incorrecta, variables no reconocidas y singularidades matemáticas.

## Tecnologías Utilizadas

* **Backend:** Python, Flask, SymPy (para cálculo simbólico y derivadas exactas).
* **Frontend:** HTML5, CSS3, JavaScript.
* **Gráficas:** Chart.js.

## Instalación y Uso

1. Instala las dependencias necesarias:
```bash
pip install flask sympy

```
2. Ejecutar el archivo
```
python taylor_app.py

```
3. Abrir el Navegador e ir a
```
http://127.0.0.1:5000
