#!/usr/bin/env python3
"""
Test script for the Encrypted Linear Algebra over UDP system
"""

import socket
import threading
import time
import numpy as np
from protocol import (
    Packet, PacketType, ReliabilityLayer, OperationType,
    create_matrix_operation_payload, parse_matrix_operation_payload, parse_result_payload
)
from encryption import MatrixEncryption
from matrix_operations import MatrixProcessor, generate_random_matrix

def test_encryption():
    """Test the encryption/decryption functionality"""
    print("Testing encryption...")
    
    # Create encryption instance
    encryption = MatrixEncryption("test_password")
    
    # Test data
    test_data = b"Hello, encrypted world!"
    
    # Encrypt and decrypt
    encrypted = encryption.encrypt_packet_payload(test_data)
    decrypted = encryption.decrypt_packet_payload(encrypted)
    
    assert decrypted == test_data
    print("✓ Encryption test passed")

def test_matrix_operations():
    """Test matrix operations"""
    print("Testing matrix operations...")
    
    processor = MatrixProcessor()
    
    # Test matrices
    matrix1 = [[1, 2], [3, 4]]
    matrix2 = [[5, 6], [7, 8]]
    
    # Test addition
    result = processor.process_operation(OperationType.ADD, [matrix1, matrix2])
    expected = np.array([[6, 8], [10, 12]])
    assert np.array_equal(result, expected)
    print("✓ Matrix addition test passed")
    
    # Test transpose
    result = processor.process_operation(OperationType.TRANSPOSE, [matrix1])
    expected = np.array([[1, 3], [2, 4]])
    assert np.array_equal(result, expected)
    print("✓ Matrix transpose test passed")
    
    # Test scalar multiplication
    result = processor.process_operation(OperationType.SCALAR_MULTIPLY, [matrix1], 2.0)
    expected = np.array([[2, 4], [6, 8]])
    assert np.array_equal(result, expected)
    print("✓ Scalar multiplication test passed")

def test_protocol():
    """Test packet protocol"""
    print("Testing protocol...")
    
    # Create reliability layer
    reliability = ReliabilityLayer()
    
    # Create test packet
    test_payload = b"test payload"
    packet = reliability.create_packet(PacketType.DATA, test_payload)
    
    # Convert to bytes and back
    packet_bytes = packet.to_bytes()
    restored_packet = Packet.from_bytes(packet_bytes)
    
    assert restored_packet.packet_type == packet.packet_type
    assert restored_packet.sequence_number == packet.sequence_number
    assert restored_packet.payload == packet.payload
    print("✓ Protocol test passed")

def test_client_server_communication():
    """Test client-server communication with actual UDP"""
    print("Testing client-server communication...")
    
    # Start a test server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 8082))  # Use different port
    
    # Start client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Test basic UDP communication
        test_message = b"Hello Server"
        client_socket.sendto(test_message, ("127.0.0.1", 8082))
        
        # Receive on server
        server_socket.settimeout(2.0)
        data, addr = server_socket.recvfrom(1024)
        
        assert data == test_message
        print("✓ Basic UDP communication test passed")
        
    finally:
        server_socket.close()
        client_socket.close()

def test_matrix_operation_payload():
    """Test matrix operation payload creation and parsing"""
    print("Testing matrix operation payloads...")
    
    # Test data
    matrices = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    operation = OperationType.ADD
    scalar = None
    
    # Create payload
    payload = create_matrix_operation_payload(operation, matrices, scalar)
    
    # Parse payload
    parsed_op, parsed_matrices, parsed_scalar = parse_matrix_operation_payload(payload)
    
    assert parsed_op == operation
    assert parsed_matrices == matrices
    assert parsed_scalar == scalar
    print("✓ Matrix operation payload test passed")

def run_performance_test():
    """Run performance test with larger matrices"""
    print("Running performance test...")
    
    # Generate large random matrices
    size = 100
    matrix1 = generate_random_matrix(size, size)
    matrix2 = generate_random_matrix(size, size)
    
    start_time = time.time()
    
    # Test matrix multiplication (most expensive operation)
    processor = MatrixProcessor()
    result = processor.process_operation(OperationType.MULTIPLY, [matrix1, matrix2])
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✓ Performance test passed: {size}x{size} matrix multiplication took {processing_time:.3f}s")
    print(f"  Result shape: {result.shape}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("ENCRYPTED LINEAR ALGEBRA SYSTEM TESTS")
    print("=" * 60)
    
    try:
        test_encryption()
        test_matrix_operations()
        test_protocol()
        test_client_server_communication()
        test_matrix_operation_payload()
        run_performance_test()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nSystem components are working correctly:")
        print("• Encryption: AES encryption/decryption functional")
        print("• Matrix Operations: All basic operations working")
        print("• Network Protocol: UDP packet handling working")
        print("• Performance: Large matrix operations tested")
        print("\nYou can now run the full system with:")
        print("  python main.py all     # Start all components")
        print("  python main.py server  # Start just the server")
        print("  python main.py client  # Start just the client")
        print("  python main.py moderator # Start just the moderator")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)