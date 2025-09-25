import struct
import json
import time
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

class PacketType(Enum):
    DATA = 1
    ACK = 2
    MATRIX_OP = 3
    RESULT = 4
    ERROR = 5

class OperationType(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    SCALAR_MULTIPLY = "scalar_multiply"
    TRANSPOSE = "transpose"
    INVERSE = "inverse"
    DETERMINANT = "determinant"
    RANK = "rank"

@dataclass
class Packet:
    packet_type: PacketType
    sequence_number: int
    timestamp: float
    payload: bytes
    checksum: int = 0
    
    def to_bytes(self) -> bytes:
        """Convert packet to bytes for transmission"""
        header = struct.pack('!IIQI', 
                           self.packet_type.value, 
                           self.sequence_number,
                           int(self.timestamp * 1000000),  # microseconds
                           len(self.payload))
        return header + self.payload
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Packet':
        """Create packet from received bytes"""
        if len(data) < 20:  # Minimum header size
            raise ValueError("Packet too short")
        
        packet_type_val, seq_num, timestamp_us, payload_len = struct.unpack('!IIQI', data[:20])
        packet_type = PacketType(packet_type_val)
        timestamp = timestamp_us / 1000000.0
        payload = data[20:20+payload_len]
        
        return cls(packet_type, seq_num, timestamp, payload)

class ReliabilityLayer:
    def __init__(self, timeout: float = 2.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.sequence_number = 0
        self.pending_acks: Dict[int, Tuple[Packet, float, int]] = {}  # seq_num -> (packet, send_time, retry_count)
    
    def get_next_sequence_number(self) -> int:
        """Get next sequence number for outgoing packet"""
        self.sequence_number += 1
        return self.sequence_number
    
    def create_packet(self, packet_type: PacketType, payload: bytes) -> Packet:
        """Create a new packet with sequence number"""
        seq_num = self.get_next_sequence_number()
        return Packet(packet_type, seq_num, time.time(), payload)
    
    def create_ack_packet(self, ack_seq_num: int) -> Packet:
        """Create an ACK packet for given sequence number"""
        payload = struct.pack('!I', ack_seq_num)
        return Packet(PacketType.ACK, 0, time.time(), payload)
    
    def add_pending_ack(self, packet: Packet):
        """Add packet to pending ACKs list"""
        self.pending_acks[packet.sequence_number] = (packet, time.time(), 0)
    
    def handle_ack(self, ack_seq_num: int) -> bool:
        """Handle received ACK"""
        if ack_seq_num in self.pending_acks:
            del self.pending_acks[ack_seq_num]
            return True
        return False
    
    def get_timed_out_packets(self) -> list:
        """Get packets that need retransmission"""
        current_time = time.time()
        timed_out = []
        
        for seq_num, (packet, send_time, retry_count) in list(self.pending_acks.items()):
            if current_time - send_time > self.timeout:
                if retry_count < self.max_retries:
                    # Update retry count and send time
                    self.pending_acks[seq_num] = (packet, current_time, retry_count + 1)
                    timed_out.append(packet)
                else:
                    # Max retries exceeded, remove from pending
                    del self.pending_acks[seq_num]
        
        return timed_out

def create_matrix_operation_payload(operation: OperationType, matrices: list, scalar: Optional[float] = None) -> bytes:
    """Create payload for matrix operation request"""
    payload_data = {
        'operation': operation.value,
        'matrices': [matrix.tolist() if hasattr(matrix, 'tolist') else matrix for matrix in matrices],
        'scalar': scalar
    }
    return json.dumps(payload_data).encode('utf-8')

def parse_matrix_operation_payload(payload: bytes) -> Tuple[OperationType, list, Optional[float]]:
    """Parse matrix operation payload"""
    data = json.loads(payload.decode('utf-8'))
    operation = OperationType(data['operation'])
    matrices = data['matrices']
    scalar = data.get('scalar')
    return operation, matrices, scalar

def create_result_payload(result: Any, success: bool = True, error_message: Optional[str] = None) -> bytes:
    """Create payload for operation result"""
    payload_data = {
        'success': success,
        'result': result.tolist() if hasattr(result, 'tolist') else result,
        'error_message': error_message
    }
    return json.dumps(payload_data).encode('utf-8')

def parse_result_payload(payload: bytes) -> Tuple[bool, Any, Optional[str]]:
    """Parse operation result payload"""
    data = json.loads(payload.decode('utf-8'))
    return data['success'], data['result'], data.get('error_message', None)