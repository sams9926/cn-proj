import socket
import threading
import time
from datetime import datetime
from protocol import Packet, PacketType

class PacketModerator:
    def __init__(self, port: int = 8081):
        self.port = port
        self.socket = None
        self.running = False
        
        # Statistics
        self.packets_observed = 0
        self.operations_observed = {}
        self.clients_seen = set()
        
    def start(self):
        """Start the packet moderator"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(("127.0.0.1", self.port))
            
            self.running = True
            print(f"Packet Moderator started on port {self.port}")
            print("Monitoring packet traffic...")
            print("-" * 60)
            print(f"{'Time':<12} {'Direction':<12} {'Client':<16} {'Type':<12} {'Seq#':<6} {'Size':<6}")
            print("-" * 60)
            
            self._monitor_loop()
            
        except Exception as e:
            print(f"Error starting moderator: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the moderator"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("\nModerator stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.socket.settimeout(1.0)
                data, addr = self.socket.recvfrom(65536)
                self._process_forwarded_packet(data)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Monitor error: {e}")
    
    def _process_forwarded_packet(self, data: bytes):
        """Process packet forwarded from server"""
        try:
            # Parse moderator header: direction|client|size|timestamp|packet_data
            parts = data.split(b"|", 4)
            if len(parts) < 5:
                return
            
            direction = parts[0].decode()
            client_addr = parts[1].decode()
            packet_size = int(parts[2].decode())
            timestamp = float(parts[3].decode())
            packet_data = parts[4]
            
            self.clients_seen.add(client_addr)
            self.packets_observed += 1
            
            # Try to parse the actual packet
            try:
                packet = Packet.from_bytes(packet_data)
                packet_type = packet.packet_type.name
                seq_num = packet.sequence_number
                
                # Track operations
                if packet.packet_type == PacketType.MATRIX_OP:
                    self.operations_observed[client_addr] = self.operations_observed.get(client_addr, 0) + 1
                
            except:
                packet_type = "UNKNOWN"
                seq_num = "?"
            
            # Format timestamp
            time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]
            
            # Print observation
            print(f"{time_str:<12} {direction:<12} {client_addr:<16} {packet_type:<12} {seq_num!s:<6} {packet_size:<6}")
            
            # Print additional info for certain packet types
            if direction == "RECEIVED" and packet_type == "MATRIX_OP":
                print(f"             └─ New matrix operation request from {client_addr}")
            elif direction == "SENT_RESULT":
                print(f"             └─ Operation result sent to {client_addr}")
            elif direction == "SENT_ERROR":
                print(f"             └─ Error response sent to {client_addr}")
                
        except Exception as e:
            print(f"Error processing forwarded packet: {e}")
    
    def print_statistics(self):
        """Print monitoring statistics"""
        print("\n" + "=" * 60)
        print("MONITORING STATISTICS")
        print("=" * 60)
        print(f"Total packets observed: {self.packets_observed}")
        print(f"Unique clients seen: {len(self.clients_seen)}")
        print(f"Clients: {', '.join(self.clients_seen) if self.clients_seen else 'None'}")
        
        if self.operations_observed:
            print("\nOperations per client:")
            for client, count in self.operations_observed.items():
                print(f"  {client}: {count} operations")
        
        print("=" * 60)

def main():
    """Main moderator entry point"""
    moderator = PacketModerator()
    
    try:
        moderator.start()
    except KeyboardInterrupt:
        print("\nShutting down moderator...")
        moderator.print_statistics()
        moderator.stop()

if __name__ == "__main__":
    main()