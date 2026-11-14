# Pattern-Based-Stabilizer-Tripwire-Quantum-Entanglement-Attack-Simulation
The purpose of the simulation is to demonstrate how error patterns can deprive Eve from learning information about the logical bits through entanglement. In standard QKD protocols, Eve can entangle an ancilla with the transmitted qubit and wait for Bob to publicly announce his basis choice. The strategy cannot work in this case.

A Qiskit simulation of a coherent CNOT entanglement attack on the **five-qubit ([[5,1,3]]) stabilizer code** under the **Pattern-Based Stabilizer Tripwire** protocol.

## Overview

In this protocol, the secret key bit does not exist prior to communication; it is dynamically formed after transmission through classical reconciliation (`a_relation` and `b_relation`). This simulation evaluates how a weight-5 CNOT entanglement attack—where Eve entangles ancillas during transit and delays measurement until after Bob finishes processing—interacts with **Pauli pattern masking** and **stabilizer error correction**:

* **Pauli Error Pattern Masking (`action = 1`):** Scrambles physical codeword parity using weight 3–5 Pauli operators, reducing Eve's extracted key information from **100% down to 50%**.
* **Stabilizer Error Correction (`noise_correction = 1`):** Extracts syndromes (`XZZXI`, `IXZZX`, `XIXZZ`, `ZXIXZ`) and applies recovery gates. Decoherence from Eve's CNOT entanglement scrambles the stabilizer phases, triggering a **50% Quantum Bit Error Rate (QBER)** alarm at Bob.

## How to Run

### Option 1: Google Colab (Recommended)
1. Open a new notebook in [Google Colab](https://google.com).
2. Run the following command in the first cell to install dependencies:
   ```bash
   !pip install qiskit qiskit-aer pandas openpyxl
   ```
3. Paste the simulation script into a new cell, set the configuration variables, and run it. The Excel output file will download automatically.

### Option 2: Local Qiskit Environment
1. Install the required Python libraries:
   ```bash
   pip install qiskit qiskit-aer numpy pandas openpyxl
   ```
2. Remove or comment out the two Google Colab lines (`from google.colab import files` and `files.download(output_filename)`).
3. Run the script via Python. The Excel report will save in your working directory.

## Configuration Variables

You can change these variables manually in the `# Initialize` section before running the code:

```python
eve_attack = 1
action = 0
measure_method = 1
noise = 0
noise_correction = 0
```

* **`eve_attack`:** `0` means Eve is not present. `1` means entanglement attack.
* **`action`:** `0` means no Pauli error pattern is used. `1` means Pauli error pattern is used.
* **`measure_method`:** `0` means measuring after decoding. `1` means measurements without decoding. It is best to keep the value at `1`.
* **`noise`:** `0` means no natural noise. `1` means natural noise.
* **`noise_correction`:** `0` means Bob doesn’t apply error correction to correct natural error. `1` means Bob applies error correction to correct natural error.

## Test Scenarios & Expected Results

1. **`eve_attack = 0` (other variables whatever their values are `0` or `1`):** Alice and Bob match 100%.
2. **`eve_attack = 1`, `action = 0`, `noise = 0`, `noise_correction = 0`:** Here, Eve collects full information of Alice through entanglement. QBER is 0%.
3. **`eve_attack = 1`, `action = 0`, `noise = 0`, `noise_correction = 1`:** Here, Eve collects full information of Alice through entanglement. QBER is 50%.
4. **`eve_attack = 1`, `action = 1`, `noise = 0`, `noise_correction = 0`:** Here, Eve matches with Alice 50% bit. QBER is 0%.
5. **`eve_attack = 1`, `action = 1`, `noise = 0`, `noise_correction = 1`:** Here, Eve matches with Alice 50% bit. QBER is 50%.

## Output File

After 100 simulated blocks, the script exports `eveattack1(5).xlsx` containing:
* **Per-block data:** Reconciled bits (`a`, `measured_a`), Eve's readout (`eve_bit`), raw bits (`given a`, `sent a`), reconciliation flags (`a relation`, `b relation`), applied Pauli masks (`given_Pauli`), channel errors (`natural_error`), and syndromes (`ancilla_bits`).
* **Aggregate statistics:** Syndrome rates (`0000`–`1111`), multi-qubit error rates, no-error rates, variance, and `eve knowledge rates`.

## Reference

* *Pattern-Based Stabilizer Tripwire* ([arXiv:2512.09672](https://arxiv.org))
