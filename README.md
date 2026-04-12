# IAGEN v2

Prototipo academico reproducible para generar planes de entrenamiento personalizados con tres condiciones experimentales:

1. `baseline_no_rag`
2. `rag_only`
3. `rag_plus_validation`

El proyecto implementa un flujo completo con:

- perfil estructurado del usuario
- corpus local y curado
- ingesta, chunking e indexacion
- retrieval semantico local
- generacion de planes en JSON
- validacion heuristica y una iteracion de repair
- demo en Streamlit
- ejecucion experimental con metricas y tablas

## Estado del proyecto

El repositorio queda funcional desde cero incluso sin Ollama gracias a un generador determinista de respaldo. Si `USE_OLLAMA=true` y el servidor esta disponible, el pipeline intentara usar el modelo local antes de recurrir al fallback.

El repositorio ahora incluye un **corpus curado descargable** basado en la revision de Deep Research, con fuentes oficiales, revisiones sistematicas abiertas y abstracts de PubMed para los articulos clave no abiertos. El corpus puede refrescarse automaticamente con [rag/download_corpus.py](/home/ndk/proyectos/clase/iagen_v2/rag/download_corpus.py).

## Estructura

```text
iagen_v2/
├── app/
├── rag/
├── data/
│   ├── raw_pdfs/
│   ├── processed/
│   ├── chunks/
│   └── profiles/
├── experiments/
├── outputs/
│   ├── plans/
│   ├── logs/
│   └── tables/
├── tests/
├── PLAN_PROYECTO.md
└── README.md
```

## Instalacion

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev,ui,rag]"
```

Configuracion opcional:

```bash
cp .env.example .env
```

## Uso rapido

1. Reingestar el corpus y ejecutar los experimentos:

```bash
.venv/bin/python rag/download_corpus.py
python experiments/run_experiments.py --rebuild-index
```

2. Lanzar la demo:

```bash
streamlit run app/ui.py
```

3. Ejecutar tests:

```bash
pytest
```

## Uso con Ollama

Si quieres usar un LLM local real:

```bash
ollama serve
ollama pull llama3.1:8b
export USE_OLLAMA=true
python experiments/run_experiments.py --rebuild-index
```

Variables de entorno relevantes:

- `USE_OLLAMA`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_FALLBACK_MODEL`
- `VECTOR_BACKEND`
## Limitaciones conocidas

- En desarrollo.
