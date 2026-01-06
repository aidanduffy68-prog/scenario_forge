# Artificial AML Data Designer

⚠️ **This project generates controlled artificial (not real) anti-money-laundering scenarios for internal testing, model evaluation, and demos. Not intended for real transaction monitoring.**

## 📌 What This Is

A toolkit to **construct realistic, adversarial crypto AML scenarios** with:
- Intent labels and provenance metadata  
- Jurisdictional context  
- Transaction graphs representing layered laundering  
- Human-readable narratives explaining each scenario  

This is **not a typical synthetic data tool** — it is a structured scenario engine designed to help:
- Stress-test AML models
- Demonstrate failure modes
- Educate analysts and regulators

## 🎯 Why It Matters

Financial AML data is typically:
- Confidential
- Restricted by privacy laws  
- Sparse for rare or evolving laundering patterns

Traditional synthetic generators focus on statistical replacement.  
This project focuses on **controlled adversarial constructs** for product validation and demos. :contentReference[oaicite:2]{index=2}

## 🚀 Features

- 🎨 Scenario templates with intent labels  
- 📊 Transaction graph outputs  
- 📑 Provenance and integrity hashes  
- 🧠 Plain-English narratives  
- 📦 JSON / CSV exporters  

## 🧪 Example Usage

```python
from scenario_forge import ScenarioForge

forge = ScenarioForge()
scenario = forge.generate("cross_chain_laundering")
scenario.export("json")
print(scenario.narrative)


