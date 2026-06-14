# Encrypted Linear Algebra over UDP with Custom Reliability Layer

A comprehensive Python-based client-server system for performing linear algebra operations on large matrices over UDP, featuring encryption, custom reliability protocols, and network simulation capabilities.

## 🚀 Features

### Core Functionality

#### Complete Linear Algebra Operations Suite

**Arithmetic Operations**

* Matrix Addition
* Matrix Subtraction
* Scalar Multiplication
* Matrix Multiplication

**Unary Operations**

* Transpose
* Inverse
* Determinant
* Rank
* Trace

**Advanced Decompositions**

* LU Decomposition
* QR Decomposition
* Singular Value Decomposition (SVD)
* Eigenvalue & Eigenvector Analysis

**System Solving**

* Gaussian Elimination
* Linear System Solver

**Vector Operations**

* Dot Product
* Vector Norms

### Network & Security

* UDP-based communication with custom reliability layer
* Dual encryption support:

  * AES-256 (fast symmetric encryption)
  * RSA-2048 (secure key exchange)
* Adaptive reliability protocols:

  * Stop-and-Wait Protocol
  * Sliding Window Protocol
* Network simulation with realistic conditions:

  * Wi-Fi
  * 3G Mobile Networks
  * High Latency Networks
  * Lossy Networks

### User Interface

* Modern GUI Client
* Material Design-inspired Interface
* Real-time Network Monitoring
* Interactive Matrix Input
* Matrix Visualization
* Comprehensive Results Display
* Export Functionality

### Monitoring & Analysis

* Packet Inspection & Logging
* Performance Metrics:

  * RTT (Round Trip Time)
  * Throughput
  * Retransmission Rates
* CSV Export Support
* Real-time Statistics Dashboard

---

## 🏗️ System Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GUI Client    │    │ Network Proxy   │    │  Matrix Server  │
│                 │    │  (Simulation)   │    │                 │
│ • Matrix Input  │◄──►│ • Packet Loss   │◄──►│ • NumPy Compute │
│ • Encryption    │    │ • Delay/Jitter  │    │ • Decryption    │
│ • Reliability   │    │ • Bandwidth     │    │ • Reliability   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                    ┌─────────────────┐
                    │   Moderator     │
                    │                 │
                    │ • Packet Logs   │
                    │ • Statistics    │
                    │ • Monitoring    │
                    └─────────────────┘
```

---

## 📦 Installation

### Prerequisites

Install project dependencies:

```bash
pip install -r requirements.txt
```

### Required Dependencies

| Package                | Purpose                 |
| ---------------------- | ----------------------- |
| numpy >= 1.24.0        | Matrix Computations     |
| scipy >= 1.11.0        | Advanced Linear Algebra |
| cryptography >= 41.0.0 | Encryption & Security   |
| matplotlib >= 3.7.0    | Visualization           |
| pandas >= 2.0.0        | Data Analysis           |
| tkinter                | GUI Framework           |

---

## 🚀 Quick Start

### Option 1: Launch Complete System

```bash
python main.py
```

This starts:

* Matrix Server
* GUI Client
* Network Simulator
* Moderator

### Option 2: Run Individual Components

#### Start Server

```bash
python main.py --component server
```

#### Start Moderator

```bash
python main.py --component moderator
```

#### Start Network Simulator

```bash
python main.py --component proxy --condition WIFI_TYPICAL
```

#### Start GUI Client

```bash
python main.py --component client
```

---

## 📋 Usage Guide

### 1. Matrix Input

Supported methods:

* Manual matrix entry
* Random matrix generation
* CSV file import
* NumPy file import
* Identity matrix templates
* Predefined matrix patterns

### 2. Operation Selection

#### Arithmetic

```text
A + B
A - B
Scalar × A
A × B
```

#### Matrix Analysis

```text
det(A)
rank(A)
trace(A)
cond(A)
```

#### Decompositions

```text
LU(A)
QR(A)
SVD(A)
Eigen(A)
```

#### Linear Systems

```text
Solve Ax = b
Gaussian Elimination
```

### 3. Network Configuration

* Default Server: localhost:12345
* Proxy Server: localhost:12346
* Reliability Mode:

  * Stop-and-Wait
  * Sliding Window
* Encryption:

  * AES
  * RSA

### 4. Results & Analysis

* Matrix Visualization
* Heatmaps
* Performance Charts
* RTT Monitoring
* Throughput Analysis
* Export to CSV, TXT, and NumPy formats

---

## 🌐 Network Simulation

### Available Profiles

| Profile      | Description                         |
| ------------ | ----------------------------------- |
| PERFECT      | 0% loss, 1–2 ms latency, 100 Mbps   |
| WIFI_TYPICAL | 3% loss, 5–25 ms latency, 50 Mbps   |
| LOSSY        | 15% loss, 10–50 ms latency, 10 Mbps |
| HIGH_LATENCY | 2% loss, 200–400 ms latency, 5 Mbps |
| MOBILE_3G    | 8% loss, 100–300 ms latency, 2 Mbps |
| UNSTABLE     | 20% loss, 20–500 ms latency, 5 Mbps |

### Example

```bash
python main.py --component proxy --condition LOSSY

python main.py --component proxy --condition HIGH_LATENCY

python main.py --component proxy --condition MOBILE_3G
```

---

## 🔒 Security Features

### Supported Encryption

#### AES-256-CBC

* Fast symmetric encryption
* Suitable for large matrix transfers

#### RSA-2048

* Secure asymmetric encryption
* OAEP padding support

### Security Practices

* Encrypted matrix transmission
* Secure IV generation
* PBKDF2 + SHA-256 key derivation
* No plaintext network communication

---

## 📊 Performance Monitoring

### Real-Time Metrics

* RTT (Round Trip Time)
* Throughput
* Retransmission Rate
* ACK Statistics
* Timeout Tracking
* Protocol Efficiency

### Export Options

* CSV Logs
* Packet Capture Records
* Performance Reports
* Statistical Summaries

---

## 🧪 Testing & Validation

### Matrix Operation Examples

```python
A = [[1, 2],
     [3, 4]]

B = [[5, 6],
     [7, 8]]
```

Supported tests:

* Matrix Addition
* Matrix Multiplication
* LU Decomposition
* SVD
* Linear System Solving

### Reliability Testing

```python
conditions = [
    "PERFECT",
    "LOSSY",
    "HIGH_LATENCY",
    "UNSTABLE"
]
```

Metrics measured:

* Packet Loss Recovery
* Retransmission Efficiency
* Error Recovery
* Protocol Adaptation

---

## 🛠️ Advanced Configuration

### Custom Network Profile

```python
custom_profile = NetworkProfile(
    packet_loss_rate=0.10,
    min_delay_ms=50,
    max_delay_ms=150,
    jitter_ms=20,
    bandwidth_kbps=5000,
    name="Custom Profile"
)
```

### Custom Server Configuration

```bash
python main.py --component server \
  --host 0.0.0.0 \
  --port 8080 \
  --encryption RSA
```

### Reliability Layer Tuning

```python
ReliabilityLayer(
    socket=udp_socket,
    mode=ProtocolMode.SLIDING_WINDOW,
    window_size=16,
    timeout=5.0,
    max_retries=3
)
```

---

## 🐛 Troubleshooting

### Connection Issues

* Verify server is running
* Check firewall settings
* Confirm correct port numbers
* Test network connectivity

### Matrix Input Errors

* Use space-separated values
* Ensure equal row lengths
* Remove invalid characters

### Performance Problems

* Use Sliding Window protocol
* Reduce matrix dimensions
* Test with different network profiles

### Encryption Errors

* Verify encryption mode matches
* Check cryptography package installation
* Confirm Python compatibility

---

## 📈 Performance Benchmarks

### Matrix Computation

| Operation        | 100×100 | 500×500 | 1000×1000 |
| ---------------- | ------- | ------- | --------- |
| Addition         | <1 ms   | 5 ms    | 20 ms     |
| Multiplication   | 2 ms    | 125 ms  | 1000 ms   |
| LU Decomposition | 3 ms    | 180 ms  | 1200 ms   |
| SVD              | 15 ms   | 800 ms  | 8000 ms   |

### Reliability Protocol Comparison

| Metric      | Stop-and-Wait | Sliding Window |
| ----------- | ------------- | -------------- |
| Latency     | Low           | Medium         |
| Throughput  | Low           | High           |
| Reliability | High          | High           |
| Complexity  | Low           | Medium         |

---

## 🤝 Contributing

Contributions are welcome.

Potential enhancements:

* Cholesky Decomposition
* Sparse Matrix Support
* ECC Encryption
* Post-Quantum Cryptography
* Real Network Interface Testing
* Large Matrix Optimizations
* Advanced GUI Tools
* Batch Processing Support

---

## 📄 License

Released under the MIT License.

See the `LICENSE` file for details.

---

## 🙏 Acknowledgments

* NumPy & SciPy — Matrix Computation Engine
* Cryptography — Secure Encryption Framework
* Matplotlib — Data Visualization
* Tkinter — Cross-platform GUI Development

---

### Project Goal

This project demonstrates secure and reliable UDP communication for distributed linear algebra computation using custom transport reliability, modern encryption techniques, and realistic network simulation environments.
