from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
from google.colab import files
import pandas as pd
import io, random
import json
from itertools import combinations, product
from qiskit.circuit.classical import expr

# define the Excel sheet
df = pd.DataFrame(columns = ["block_id","a","measured_a","eve_bit","eve","attack_type","given a","sent a","a relation","b relation","given_Pauli","natural_error","ancilla_bits" ,"variance", "0000", "0001","0010","0011","0100", "0101","0110","0111", "1000","1001", "1010","1011", "1100","1101", "1110","1111","multi0000", "multi0001","multi0010","multi0011","multi0100", "multi0101","multi0110","multi0111", "multi1000","multi1001", "multi1010","multi1011", "multi1100","multi1101", "multi1110","multi1111","multi_qubit_error_rates","no_error_rates"])

def make_circuit():
  qr = QuantumRegister(15)
  cr = ClassicalRegister(10)
  qc = QuantumCircuit(qr, cr)
  return qc, qr, cr

def QKD_encoder(qc, qr, cr, person):
  if person == 0: # Alice chooses logical qubit
   if a == 1:
       qc.x(qr[0])


  # apply 5 qubit encoder
  qc.x(qr[1])
  qc.x(qr[4])
  qc.cx(qr[0], qr[1])
  qc.h(qr[1])
  qc.h(qr[2])
  qc.cx(qr[2], qr[0])
  qc.cx(qr[2], qr[3])
  qc.cx(qr[1], qr[3])
  qc.cx(qr[0], qr[4])
  qc.cx(qr[1], qr[0])
  qc.h(qr[3])
  qc.h(qr[4])
  qc.cx(qr[3], qr[0])
  qc.cx(qr[4], qr[0])


  if action == 1: # Alice applies weight 3 to 5 Pauli errors
   for qubit_idx, axis in enumerate(axes):
     qc, qr, cr = bit_and_phase_flip(qc, qr, cr, flip_qubit=qubit_idx, rand_axis=axis)

   qc.swap(qr[0], qr[3]) # Alice checks the syndrome after learning the pattern from Bob, for inconvenience we are taking the measurement without lookup table prior to Bob informing
   qc.swap(qr[1], qr[2])

   qc,qr,cr = decoding(qc, qr, cr)
   for i in range(4):
     qc.store(cr[6 + i], cr[i])
 
   qc.swap(qr[0], qr[3])
   qc.swap(qr[1], qr[2])
  return qc, qr, cr

def bit_and_phase_flip(qc, qr, cr, flip_qubit, rand_axis):
  # choose x,y,z error
  if rand_axis == 0:
    qc.x(qr[flip_qubit])
  elif rand_axis == 1:
    qc.z(qr[flip_qubit])
  elif rand_axis == 2:
    qc.x(qr[flip_qubit])
    qc.z(qr[flip_qubit])
  return qc, qr, cr

def measurements(qc, qr, cr, person):

  c1 = random.randint(0, 1)
  c2 = 1 if c1 == 0 else random.randint(0, 1)
  s_part = 0

  # Bob applies error correction to correct natural error
  qc.swap(qr[0], qr[3])
  qc.swap(qr[1], qr[2])
  qc, qr, cr = decoding(qc, qr, cr)

  #Alice sends the total syndrome after Bob sends his measured syndrome
  if action == 1:
    for i in range(4):
      xor_val = expr.bit_xor(cr[i], cr[6 + i])
      qc.store(cr[i], xor_val)
    for i in range(4):
      qc.store(cr[6 + i], False)

  mappingX = {1:1, 8:2, 12:3, 6:4, 3:5, 11:1, 13:2, 14:3, 15:4, 7:5}
  mappingZ = {10:1, 5:2, 2:3, 9:4, 4:5, 11:1, 13:2, 14:3, 15:4, 7:5}
  syndrome_to_qubit = {
      1: 1, 10: 1, 11: 1,
      8: 2,  5: 2, 13: 2,
      12: 3, 2: 3, 14: 3,
      6: 4,  9: 4, 15: 4,
      3: 5,  4: 5,  7: 5
  }

  if c1 == 0:
    s_part = np.random.randint(0, 2)
    target_vals = [1, 3, 6, 7, 8, 11, 12, 13, 14, 15]

    for val in target_vals:
      with qc.if_test((cr, val)):
        qc.x(qr[14])

    qc.measure(qr[14], cr[6])

    flip_q2 = np.random.randint(0, 5)
    flip_a2 = 1 if s_part == 0 else random.choice([0, 2])
    qc, qr, cr = bit_and_phase_flip(qc, qr, cr, flip_q2, flip_a2)

  elif c1 == 1 and c2 == 0:
    for val, qubit_index in mappingX.items():
      circuit1 = QuantumCircuit(qr, cr)
      circuit1.x(qr[qubit_index - 1])
      qc.if_test((cr, val), circuit1, qubits=qr, clbits=cr)

    for val, qubit_index in mappingZ.items():
      circuit2 = QuantumCircuit(qr, cr)
      circuit2.z(qr[qubit_index - 1])
      qc.if_test((cr, val), circuit2, qubits=qr, clbits=cr)

  elif c1 == 1 and c2 == 1:
    s_part = np.random.randint(0, 2)

    for val, qubit_index in mappingX.items():
      circuit1 = QuantumCircuit(qr, cr)
      circuit1.x(qr[qubit_index - 1])
      qc.if_test((cr, val), circuit1, qubits=qr, clbits=cr)

    for val, qubit_index in mappingZ.items():
      circuit2 = QuantumCircuit(qr, cr)
      circuit2.z(qr[qubit_index - 1])
      qc.if_test((cr, val), circuit2, qubits=qr, clbits=cr)

    flip_a2 = 1 if s_part == 0 else random.choice([0, 2])
    for val, qubit_index in syndrome_to_qubit.items():
      circuit_spart = QuantumCircuit(qr, cr)
      circuit_spart, qr, cr = bit_and_phase_flip(circuit_spart, qr, cr, qubit_index - 1, flip_a2)
      qc.if_test((cr, val), circuit_spart, qubits=qr, clbits=cr)

    fallback_q = np.random.randint(0, 5)
    circuit_no_noise = QuantumCircuit(qr, cr)
    circuit_no_noise, qr, cr = bit_and_phase_flip(circuit_no_noise, qr, cr, fallback_q, flip_a2)
    qc.if_test((cr, 0), circuit_no_noise, qubits=qr, clbits=cr)

  if measure_method == 0: # with decoding

    qc, qr, cr = decoding_circuit(qc, qr, cr, 0)
  elif measure_method == 1: # without decoding
    qc, qr, cr = without_decoding_circuit(qc, qr, cr, 0)

  return qc, qr, cr, s_part

def without_decoding_circuit(qc,qr,cr,person):
  qc.reset(qr[5])
  if person == 0:
    for i in range(5):
       qc.measure(qr[i], cr[9])
       qc.cx(qr[i], qr[5])
    qc.measure(qr[5],cr[4])

  elif person == 2:
    for i in range(5):
       qc.measure(qr[i+9], cr[9])
       qc.cx(qr[i+9], qr[5])
    qc.measure(qr[5],cr[5])

  return qc,qr,cr

def decoding_circuit(qc,qr,cr,person):
  qc.cx(qr[4], qr[0])
  qc.cx(qr[3], qr[0])
  qc.h(qr[4])
  qc.h(qr[3])
  qc.cx(qr[1], qr[0])
  qc.cx(qr[0], qr[4])
  qc.cx(qr[1], qr[3])
  qc.cx(qr[2], qr[3])
  qc.cx(qr[2], qr[0])
  qc.h(qr[2])
  qc.h(qr[1])
  qc.cx(qr[0],qr[1])
  qc.x(qr[4])
  qc.x(qr[1])

  if person == 0:
    qc.measure(qr[0],cr[4])
  elif person == 2:
    qc.measure(qr[0],cr[5])
  return qc,qr,cr

def decoding(qc, qr, cr):
  # g1 syndrome: XZZXI
  qc.reset(qr[5])
  qc.h(qr[0]); qc.cx(qr[0], qr[5]); qc.h(qr[0])
  qc.cx(qr[1], qr[5])
  qc.cx(qr[2], qr[5])
  qc.h(qr[3]); qc.cx(qr[3], qr[5]); qc.h(qr[3])
  qc.barrier()

  # g2 syndrome: IXZZX
  qc.reset(qr[6])
  qc.h(qr[1]); qc.cx(qr[1], qr[6]); qc.h(qr[1])
  qc.cx(qr[2], qr[6])
  qc.cx(qr[3], qr[6])
  qc.h(qr[4]); qc.cx(qr[4], qr[6]); qc.h(qr[4])
  qc.barrier()

  # g3 syndrome: XIXZZ
  qc.reset(qr[7])
  qc.h(qr[0]); qc.cx(qr[0], qr[7]); qc.h(qr[0])
  qc.h(qr[2]); qc.cx(qr[2], qr[7]); qc.h(qr[2])
  qc.cx(qr[3], qr[7])
  qc.cx(qr[4], qr[7])
  qc.barrier()

  # g4 syndrome: ZXIXZ
  qc.reset(qr[8])
  qc.cx(qr[0], qr[8])
  qc.h(qr[1]); qc.cx(qr[1], qr[8]); qc.h(qr[1])
  qc.h(qr[3]); qc.cx(qr[3], qr[8]); qc.h(qr[3])
  qc.cx(qr[4], qr[8])
  qc.barrier()

  # measure ancillas to get syndrome measurements
  qc.measure([qr[5], qr[6], qr[7], qr[8]], [cr[3], cr[2], cr[1], cr[0]])
  return qc, qr, cr


def eve_apply(qc,qr,cr):
  qc.cx(qr[0],qr[9])
  qc.cx(qr[1],qr[10])
  qc.cx(qr[2],qr[11])
  qc.cx(qr[3],qr[12])
  qc.cx(qr[4],qr[13])

  return qc,qr,cr

def eve_apply_case2(qc, qr, cr, use_decoy):
  qc.reset(qr[9])
  for i in range(5):
      qc.cx(qr[i], qr[9])

  return qc,qr,cr

# Initialize

eve_attack = 1
action = 1
measure_method = 1
noise = 0

if eve_attack == 0:
   eve_x = 0
else:
   eve_x = 1

for p in range(100):

   a = np.random.randint(0,2)
   a_relation = np.random.randint(0,2)
   b_relation = np.random.randint(0,2)
   totalxy = 0


   axes = []
   if action == 1:
    while len(axes) < 5:
      if len(axes) < 4:
       choice = random.randint(0, 3)
       if choice == 3 and axes.count(3) >= 2:
          continue
      else:
        # Check if the current count of {0, 2} matches the required parity
        if totalxy % 2 == a_relation:
            # Parity is already satisfied, so we must pick from {1, 3}
            valid_choices = [1, 3] if axes.count(3) < 2 else [1]
        else:
            # Parity is not satisfied, so we must pick from {0, 2}
            valid_choices = [0, 2]

        choice = random.choice(valid_choices)

      if choice in (0, 2):
         totalxy += 1
      axes.append(choice)

   qc, qr, cr = make_circuit()
   qc, qr, cr= QKD_encoder(qc, qr, cr, 0)

   if noise == 1:
      flip_q = np.random.randint(0,5)
      rand_a = np.random.randint(0,3)
      qc, qr, cr = bit_and_phase_flip(qc, qr, cr, flip_q, rand_a)
   elif noise == 0:
      flip_q = 3
      rand_a = 3
   if eve_attack == 1:
      qc, qr, cr = eve_apply(qc,qr,cr)
   elif eve_attack == 2:
      qc, qr, cr = eve_apply_case2(qc, qr, cr, use_decoy=0)
   qc,qr,cr,s_part = measurements(qc,qr,cr,0)
   if eve_attack == 1:
      qc,qr,cr = without_decoding_circuit(qc,qr,cr,2)
   elif eve_attack == 2:
      qc.measure(qr[9], cr[5])
   simulation = AerSimulator()
   qc_transpiled = transpile(qc, simulation)
   for q in range(1):
          result = simulation.run(qc_transpiled, shots=1, memory=True).result()
          memory = result.get_memory()
          ancilla_bits =[6,7,8,9]

   gate_map = {0: 'X', 1: 'Z', 2: 'Y', 3: 'I'}

   string_a = "".join([gate_map[num] for num in axes])

   base_list = ['I'] * 5
   base_list[flip_q] = gate_map[rand_a]
   natural_error_string = "".join(base_list)

   a_bit = [5]
   eve_bit = [4]
   c_value = [3]
   a_memory =[]
   for outcome in memory:
      key = ' ' .join(outcome[i] for i in a_bit)
      a_memory.append(key)

   eve_memory = []
   for outcome in memory:
       key = '' .join(outcome[i] for i in eve_bit)
       eve_memory.append(key)

   marginal_memory =[]
   for outcome in memory:
      key = '' .join(outcome[i] for i in ancilla_bits)
      marginal_memory.append(int(key,2))

   c_memory = []
   for outcome in memory:
       key = '' .join(outcome[i] for i in c_value)
       c_memory.append(key)

   a_str =  ''.join(a_memory)
   eve_str = ''.join(eve_memory)
   c_str = ''.join(c_memory)

   int_a = int(a_str,2)
   c_val = int(c_str,2)
   int_eve_bit = int(eve_str,2)

   if action == 1:

    if b_relation == 1:
     if int_a == 0:
      bob_bit = 1
     else:
      bob_bit = 0
    else:
     bob_bit = int_a
    if a_relation == b_relation:
     alice_bit = a
    else:
     if a == 0:
      alice_bit = 1
     else:
      alice_bit = 0
    if s_part == 1:
     if alice_bit == 0:
      alice_bit = 1
     else:
      alice_bit = 0
    if c_val == 1:
     if alice_bit == 0:
      alice_bit = 1
     else:
      alice_bit = 0
   else:
     bob_bit = int_a
     alice_bit = a

   

   int_ancilla = marginal_memory[0]
   df.loc[len(df)] = [p,alice_bit,bob_bit,int_eve_bit,eve_x,eve_attack,a,int_a,a_relation,b_relation,string_a,natural_error_string,int_ancilla,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]

#calculation

ancilla_counts = df["ancilla_bits"].value_counts()

mask = (df["a"] != df["measured_a"])
mask1 = (df["a"] == df["eve_bit"])
multi_ancilla_counts = df.loc[mask, "ancilla_bits"].value_counts()

eve_bit_counts = df.loc[mask1, "ancilla_bits"].value_counts()

qubit_list1 = ["0000", "0001","0010","0011","0100", "0101","0110","0111", "1000","1001", "1010","1011", "1100","1101", "1110","1111"]
qubit_list2 = ["multi0000", "multi0001","multi0010","multi0011","multi0100", "multi0101","multi0110","multi0111", "multi1000","multi1001", "multi1010","multi1011", "multi1100","multi1101", "multi1110","multi1111"]

total_an = ancilla_counts.sum()
eve_knowledge_rates = eve_bit_counts.sum()/total_an

for i, item in enumerate(qubit_list1):

  a_c_rates = ancilla_counts.get(i,0)/total_an
  df[item] = a_c_rates

for i, item in enumerate(qubit_list2):

  a_c_rates = multi_ancilla_counts.get(i,0)/total_an
  df[item] = a_c_rates

df["multi_qubit_error_rates"] = multi_ancilla_counts.sum()/total_an
no_E_rate = (ancilla_counts.get(0,0) - multi_ancilla_counts.get(0,0))/total_an

df["no_error_rates"] = no_E_rate
var_val = (no_E_rate * (1 - no_E_rate))/ total_an

print(" var_val", var_val)
df["variance"] = var_val

df["eve knowledge rates"] = eve_knowledge_rates

print(" ancilla_counts ",ancilla_counts.sum())
print(" multi ancilla counts ", multi_ancilla_counts.sum())
print(" multi ancilla counts 0000", multi_ancilla_counts.get(0,0))

output_filename = "eveattack1(5).xlsx"
df.to_excel(output_filename, index=False)
files.download(output_filename)

#
