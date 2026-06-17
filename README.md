# Q-EOS: Qwen Economic Agent Society

> A multi‑agent economic governance system powered by Qwen, PID control, and a three‑layer safety framework.

Q-EOS is a **fully autonomous multi‑agent system** that governs a token economy using:

- **5 specialized agents** (Observer, Risk, PID, Treasury, Governor)  
- **Qwen 3.7‑Max** for transparent governance reasoning  
- **PID controller** for stable intervention  
- **Hard constraint layer** for treasury protection  

It demonstrates how AI agents can collaborate to stabilize a digital asset, while maintaining safety and explainability.

---

## 🏗️ System Architecture

| Agent | Role |
|-------|------|
| **Observer** | Fetches current market price |
| **Risk** | Calculates risk score based on price deviation |
| **PID** | Computes optimal intervention strength (buyback/sell) |
| **Governor** | Qwen‑powered, decides `APPROVE` or `REJECT` with detailed reasoning |
| **Treasury** | Executes only approved actions, enforces hard constraints (10% per tx, emergency stops) |

---

## 🧠 Key Features

### 1. Multi‑Agent Society
Five agents work as a **committee** – each with a distinct role – to make collective governance decisions.

### 2. Qwen‑Driven Governance
Every proposal is reviewed by Qwen with a **human‑readable rationale**. Example:[Qwen] APPROVE Risk=LOW
[Reason] Market price 0.9741 falls within the moderate deviation range (0.95-0.98), triggering a multiplier of 1.0; risk score 20 is low, and treasury balance is sufficient to support intervention.

---


### 3. PID Controller
A classic feedback‑control loop continuously adjusts intervention intensity, reducing price volatility.

### 4. Three‑Layer Safety
- **PID layer**: calculates ideal action  
- **Qwen layer**: makes the final `APPROVE/REJECT` decision  
- **Treasury layer**: imposes hard limits (≤10% of balance per tx, extreme‑price pause)

### 5. Quantifiable Results (365‑day simulation)
- **Average rejection rate**: 64.5% (system actively prevents risky operations)  
- **Final treasury balance**: 37,306 USDC (protected from bankruptcy)  
- **Governance efficiency score**: 88.7/100  
- **Overall stability score**: 49.8/100 (price volatility remains a challenge, but treasury is safe)

![Governance Analysis](docs/governance_analysis.png)

---

## 🏗️ System Architecture

![System Architecture](docs/architecture.png)

| Agent | Role |
|-------|------|
| **Observer** | Fetches current market price |
| **Risk** | Calculates risk score based on price deviation |
| **PID** | Computes optimal intervention strength (buyback/sell) |
| **Governor** | Qwen‑powered, decides `APPROVE` or `REJECT` with detailed reasoning |
| **Treasury** | Executes only approved actions, enforces hard constraints (10% per tx, emergency stops) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- An [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/) account with Qwen API access

### Installation
```bash
git clone https://github.com/your-username/Q-EOS.git
cd Q-EOS
pip install -r requirements.txt
```

### Prerequisites
- Open config.py in the root directory.
- Replace your-api-key-here with your Qwen API key:QWEN_API_KEY = "sk-xxxxxxxxxxxxxxxx"
- Save the file.

### Run 30‑day demonstration (with Qwen reasoning)
```bash
python simulation_demo.py
```

### Run 365‑day simulation (for analysis)
```bash
python simulation.py
python analysis.py
```

## 📁 Repository Structure

```
Q-EOS/
├── agents/            # Five agent implementations
├── core/              # Message bus, PID controller, config
├── market.py          # Market simulator with shocks and feedback
├── simulation.py      # 365‑day fast simulation (for submission)
├── simulation_demo.py # 30‑day Qwen‑enabled demo (for video)
├── analysis.py        # Generates governance dashboard
├── plot_price.py      # Price and treasury curves
├── requirements.txt   # Dependencies
├── README.md
├── LICENSE            # MIT
└── config.py          # Configuration file (replace your-api-key-here)
```

## 📊 Results

### Governance Rejection Rate
Over 365 days, Qwen‑Governor rejected **64.5%** of proposals, demonstrating strong risk awareness.

### Treasury Protection
The treasury declined from 50,000 to 37,306 – but **never crashed** thanks to the hard constraint layer.

### Heatmap
Interventions (blue = approved, red = rejected) show that the system **buys low and sells high** – the intended behaviour.

![Treasury Curve](docs/treasury_curve.png)

---

## 🛠️ Technology Stack

| Component | Tool |
|-----------|------|
| Language Model | Qwen 3.7‑Max (via Alibaba Cloud Bailian) |
| Framework | Python + custom MessageBus |
| Control | PID controller |
| Visualisation | Matplotlib, Pandas |
| Deployment | Alibaba Cloud ECS |

---

## 🔮 Future Work

- Add **on‑chain execution** for real DeFi protocols  
- Incorporate **incentive mechanisms** (e.g., transaction fees) to sustain treasury  
- Evolve agents with **individual memory** for adaptive learning  
- Support **cross‑ecosystem governance** for multiple token economies

---

## 📄 License

MIT – see [LICENSE](LICENSE) for details.

## 🙌 Acknowledgements

- Built for the **Qwen Cloud Hackathon 2026** – Agent Society Track  
- Inspired by DCBM (Dynamic Control Buyback Mechanism, arXiv:2601.08399)
