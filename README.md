# modelc

A ready-to-run Python CLI skeleton for portable, inspectable AI model containers.

This project implements a practical v0 of the `modelc` specification with:

- `modelc build`
- `modelc run`
- `modelc inspect`

It supports:
- manifest parsing from `model.yaml`
- packaging local projects into `.modelc.tar.gz`
- running local projects or packaged artifacts
- input/output schema validation
- a simple Python entrypoint contract using `stdin` and `stdout`

## Quick start

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Try the example

Inspect the example:

```bash
modelc inspect examples/sentiment-basic
```

Build it:

```bash
modelc build examples/sentiment-basic
```

Run it from source:

```bash
modelc run examples/sentiment-basic --input '{"text":"I love this"}'
```

Run it from the built package:

```bash
modelc run examples/sentiment-basic/dist/sentiment-basic-0.1.0.modelc.tar.gz --input '{"text":"This is bad"}'
```

## Manifest shape

```yaml
apiVersion: modelc.dev/v0
kind: ModelContainer

metadata:
  name: sentiment-basic
  version: 0.1.0
  description: Basic sentiment classifier

runtime:
  type: python
  version: "3.11"
  dependencies: []

artifacts:
  weights:
    path: ./model/
    format: pytorch

  tokenizer:
    path: ./tokenizer/
    format: huggingface

interface:
  input:
    type: text
    schema:
      text: string

  output:
    type: classification
    schema:
      label: string
      confidence: float

entrypoint:
  command: python run.py
```

## Entrypoint contract

The entrypoint must:
- read JSON from `stdin`
- write JSON to `stdout`
- write logs/errors to `stderr`
- exit non-zero on failure

## Notes

This is a deliberately small v0 implementation.

It does **not**:
- create virtual environments
- install dependencies automatically
- support non-Python runtimes
- provide remote registry support
- implement signing or provenance

## License

MIT
