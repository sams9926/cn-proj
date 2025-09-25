import socket
import threading
import time
import traceback
from typing import Dict, Set, Optional

from protocol import (
    Packet, PacketType, ReliabilityLayer, 
    parse_matrix_operation_payload, create_result_payload
)
from encryption import MatrixEncryption
from matrix_operations import MatrixProcessor

class UDPMatrixServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, moderator_port: int = 8081):
        self.host = host
        self.port = port
        self.moderator_port = moderator_port
        self.socket = None
        self.running = False
        self.clients: Dict[str, ReliabilityLayer] = {}
        self.encryption = MatrixEncryption()
        self.processor = MatrixProcessor()
        self.moderator_socket = None
        
        # Statistics
        self.packets_received = 0
        self.packets_sent = 0
        self.operations_processed = 0
        
    def start(self):
        """Start the UDP server"""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            
            # Create moderator socket for forwarding packets
            self.moderator_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.running = True
            print(f"Matrix Server started on {self.host}:{self.port}")
            print(f"Forwarding packets to Moderator on port {self.moderator_port}")
            print(f"Encryption: {self.encryption.get_encryption_info()}")
            
            # Start main server loop
            self._server_loop()
            
        except Exception as e:
            print(f"Error starting server: {e}")
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Stop the UDP server"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.moderator_socket:
            self.moderator_socket.close()
        print("Server stopped")
    
    def _server_loop(self):
        """Main server loop"""
        while self.running:
            try:
                # Receive data with timeout
                self.socket.settimeout(1.0)
                data, client_addr = self.socket.recvfrom(65536)
                self.packets_received += 1
                
                # Forward to moderator for observation
                self._forward_to_moderator(data, client_addr, "RECEIVED")
                
                # Process packet in separate thread
                thread = threading.Thread(target=self._process_packet, args=(data, client_addr))
                thread.daemon = True
                thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in server loop: {e}")
    
    def _process_packet(self, data: bytes, client_addr: tuple):
        """Process received packet"""
        try:
            # Parse packet
            packet = Packet.from_bytes(data)
            client_id = f"{client_addr[0]}:{client_addr[1]}"
            
            # Initialize client reliability layer if needed
            if client_id not in self.clients:
                self.clients[client_id] = ReliabilityLayer()
            
            reliability = self.clients[client_id]
            
            print(f"Received packet from {client_id}: Type={packet.packet_type.name}, Seq={packet.sequence_number}")
            
            if packet.packet_type == PacketType.MATRIX_OP:
                # Send ACK first
                ack_packet = reliability.create_ack_packet(packet.sequence_number)
                ack_data = ack_packet.to_bytes()
                self.socket.sendto(ack_data, client_addr)
                self._forward_to_moderator(ack_data, client_addr, "SENT_ACK")
                
                # Decrypt and process matrix operation
                try:
                    decrypted_payload = self.encryption.decrypt_packet_payload(packet.payload)
                    operation, matrices, scalar = parse_matrix_operation_payload(decrypted_payload)
                    
                    print(f"Processing {operation.value} operation for {client_id}")
                    
                    # Perform operation
                    result = self.processor.process_operation(operation, matrices, scalar)
                    self.operations_processed += 1
                    
                    # Create result packet
                    result_payload = create_result_payload(result, success=True)
                    encrypted_result = self.encryption.encrypt_packet_payload(result_payload)
                    
                    result_packet = reliability.create_packet(PacketType.RESULT, encrypted_result)
                    result_data = result_packet.to_bytes()
                    
                    # Send result
                    self.socket.sendto(result_data, client_addr)
                    self.packets_sent += 1
                    self._forward_to_moderator(result_data, client_addr, "SENT_RESULT")
                    
                    print(f"Sent result to {client_id}")
                    
                except Exception as op_error:
                    # Send error response
                    error_payload = create_result_payload(None, success=False, error_message=str(op_error))
                    encrypted_error = self.encryption.encrypt_packet_payload(error_payload)
                    
                    error_packet = reliability.create_packet(PacketType.ERROR, encrypted_error)
                    error_data = error_packet.to_bytes()
                    
                    self.socket.sendto(error_data, client_addr)
                    self.packets_sent += 1
                    self._forward_to_moderator(error_data, client_addr, "SENT_ERROR")
                    
                    print(f"Sent error to {client_id}: {op_error}")
            
            elif packet.packet_type == PacketType.ACK:
                # Handle ACK from client (for our sent packets)
                print(f"Received ACK from {client_id}")
                
        except Exception as e:
            print(f"Error processing packet from {client_addr}: {e}")
            traceback.print_exc()
    
    def _forward_to_moderator(self, data: bytes, client_addr: tuple, direction: str):
        """Forward packet to moderator for observation"""
        try:
            moderator_addr = ("127.0.0.1", self.moderator_port)
            
            # Create moderator info
            info = f"{direction}|{client_addr[0]}:{client_addr[1]}|{len(data)}|{time.time()}"
            moderator_data = info.encode() + b"|" + data
            
            self.moderator_socket.sendto(moderator_data, moderator_addr)
            
        except Exception as e:
            # Don't let moderator errors stop server operation
            pass
    
    def get_stats(self):
        """Get server statistics"""
        return {
            'packets_received': self.packets_received,
            'packets_sent': self.packets_sent,
            'operations_processed': self.operations_processed,
            'active_clients': len(self.clients)
        }

def main():
    """Main server entry point"""
    server = UDPMatrixServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main()