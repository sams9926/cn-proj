# Overview

This project implements an encrypted linear algebra computation system using UDP communication with a custom reliability layer. The system consists of three main components: a UDP server that processes matrix operations, a GUI client that submits operations, and a packet moderator that observes network traffic. All matrix data is encrypted using AES encryption before transmission, and the system supports various linear algebra operations including matrix addition, multiplication, transpose, inverse, determinant, and rank calculations.

## Current Status
The MVP system is fully implemented and tested with all core functionality working:
- ✅ AES encryption/decryption for matrix data transmission
- ✅ UDP packet protocol with sequence numbers and ACKs
- ✅ Server processing all basic matrix operations (add, subtract, multiply, transpose, inverse, determinant, rank, scalar multiply)
- ✅ Client with Tkinter GUI for matrix input and operation selection
- ✅ Packet moderator for network traffic observation
- ✅ Stop-and-Wait reliability protocol foundation
- ✅ Comprehensive test suite covering all components
- ✅ Launch system for running individual components or all together

## Recent Changes
- December 25, 2025: Complete system implementation with working UDP server, Tkinter client, packet moderator, and comprehensive testing framework
- Fixed packet protocol structure for consistent header serialization
- Implemented all basic linear algebra operations with proper error handling
- Added system launcher that can run individual components or complete system

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Client-Server Architecture
The system uses a UDP-based client-server model with three distinct components:
- **Client**: Tkinter-based GUI application that sends encrypted matrix operations
- **Server**: UDP server that processes matrix computations using NumPy
- **Moderator**: Passive observer that monitors packet traffic for demonstration purposes

## Custom Reliability Layer
Since UDP is unreliable, the system implements a custom reliability mechanism:
- **Sequence numbering**: Each packet has a unique sequence number for ordering
- **Acknowledgments**: Server sends ACK packets to confirm receipt
- **Retransmission**: Client retransmits packets on timeout using exponential backoff
- **Stop-and-Wait protocol**: Initially uses simple stop-and-wait, designed to upgrade to sliding window

## Encryption System
The system uses AES encryption for all matrix data:
- **Key derivation**: PBKDF2 with SHA256 for password-based key generation
- **Symmetric encryption**: Fernet (AES 128 in CBC mode) for payload encryption
- **Fixed salt**: Uses stable salt for demonstration (production would use random salts)

## Matrix Operations Engine
Built on NumPy for high-performance linear algebra:
- **Basic operations**: Addition, subtraction, multiplication, scalar multiplication
- **Advanced operations**: Transpose, inverse, determinant, rank calculation
- **Support for**: LU decomposition, SVD, eigenvalue/eigenvector computation
- **Error handling**: Validates matrix dimensions and mathematical constraints

## Protocol Design
Custom packet structure with:
- **Header format**: Fixed 20-byte header with type, sequence, timestamp, payload length
- **Packet types**: DATA, ACK, MATRIX_OP, RESULT, ERROR
- **Operation encoding**: JSON-based payload structure for matrix operations
- **Checksum validation**: For packet integrity verification

## GUI Architecture
Tkinter-based client interface:
- **Matrix input**: Text areas for manual matrix entry or random generation
- **Operation selection**: Dropdown menus for operation types
- **Real-time status**: Status updates and progress indicators
- **Result display**: Scrollable text area for operation results

# External Dependencies

## Core Libraries
- **NumPy**: Matrix operations and linear algebra computations
- **Tkinter**: GUI framework for client interface (built into Python)
- **Socket**: UDP networking (built into Python standard library)
- **Threading**: Concurrent packet handling and GUI responsiveness

## Cryptography
- **cryptography**: AES encryption using Fernet symmetric encryption
- **PBKDF2HMAC**: Key derivation from passwords
- **SHA256**: Hashing algorithm for key derivation

## Data Handling
- **JSON**: Serialization of matrix operation payloads
- **Struct**: Binary packet header packing/unpacking
- **Base64**: Encoding for encryption key management

## System Integration
- **Subprocess**: For launching multiple system components simultaneously
- **Time**: Timestamp generation and timeout handling
- **Traceback**: Error logging and debugging support