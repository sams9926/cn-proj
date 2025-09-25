import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import time
import json
from typing import Optional, List
import numpy as np

from protocol import (
    Packet, PacketType, ReliabilityLayer, OperationType,
    create_matrix_operation_payload, parse_result_payload
)
from encryption import MatrixEncryption
from matrix_operations import generate_random_matrix, create_identity_matrix

class MatrixClient:
    def __init__(self, server_host: str = "127.0.0.1", server_port: int = 8080):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.reliability = ReliabilityLayer()
        self.encryption = MatrixEncryption()
        
        # GUI components
        self.root = None
        self.result_text = None
        self.status_label = None
        
        # Current operation state
        self.waiting_for_response = False
        self.current_operation = None
        
    def start_gui(self):
        """Start the GUI application"""
        self.root = tk.Tk()
        self.root.title("Encrypted Matrix Operations over UDP")
        self.root.geometry("800x600")
        
        self._create_gui()
        self._setup_networking()
        
        self.root.mainloop()
    
    def _create_gui(self):
        """Create the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Encrypted Linear Algebra over UDP", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Operation selection
        ttk.Label(main_frame, text="Operation:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.operation_var = tk.StringVar(value="add")
        operation_combo = ttk.Combobox(main_frame, textvariable=self.operation_var, 
                                     values=["add", "subtract", "multiply", "scalar_multiply", 
                                           "transpose", "inverse", "determinant", "rank"])
        operation_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Matrix input methods
        ttk.Label(main_frame, text="Matrix Input:").grid(row=2, column=0, sticky=tk.W, pady=5)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(input_frame, text="Manual Entry", command=self._manual_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Random 3x3", command=lambda: self._generate_random(3, 3)).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Random 5x5", command=lambda: self._generate_random(5, 5)).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Identity 3x3", command=lambda: self._generate_identity(3)).pack(side=tk.LEFT, padx=5)
        
        # Scalar input (for scalar multiplication)
        ttk.Label(main_frame, text="Scalar Value:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.scalar_var = tk.StringVar(value="2.0")
        scalar_entry = ttk.Entry(main_frame, textvariable=self.scalar_var)
        scalar_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Matrix display areas
        ttk.Label(main_frame, text="Matrix 1:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        self.matrix1_text = scrolledtext.ScrolledText(main_frame, height=8, width=30)
        self.matrix1_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Matrix 2:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        self.matrix2_text = scrolledtext.ScrolledText(main_frame, height=8, width=30)
        self.matrix2_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Execute Operation", command=self._execute_operation).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear Results", command=self._clear_results).pack(side=tk.LEFT, padx=10)
        
        # Results area
        ttk.Label(main_frame, text="Results:").grid(row=7, column=0, sticky=(tk.W, tk.N), pady=5)
        self.result_text = scrolledtext.ScrolledText(main_frame, height=10, width=50)
        self.result_text.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Initialize with sample matrices
        self._generate_random(3, 3)
    
    def _setup_networking(self):
        """Setup UDP networking"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)
            self._update_status("Network ready - Encryption enabled")
        except Exception as e:
            self._update_status(f"Network error: {e}")
    
    def _manual_entry(self):
        """Open manual matrix entry dialog"""
        dialog = MatrixEntryDialog(self.root)
        if dialog.result:
            self.matrix1_text.delete(1.0, tk.END)
            self.matrix1_text.insert(1.0, self._format_matrix_display(dialog.result))
    
    def _generate_random(self, rows: int, cols: int):
        """Generate random matrices"""
        matrix1 = generate_random_matrix(rows, cols, -10, 10)
        matrix2 = generate_random_matrix(rows, cols, -10, 10)
        
        self.matrix1_text.delete(1.0, tk.END)
        self.matrix1_text.insert(1.0, self._format_matrix_display(matrix1))
        
        self.matrix2_text.delete(1.0, tk.END)
        self.matrix2_text.insert(1.0, self._format_matrix_display(matrix2))
        
        self._update_status(f"Generated random {rows}x{cols} matrices")
    
    def _generate_identity(self, size: int):
        """Generate identity matrix"""
        identity = create_identity_matrix(size)
        self.matrix1_text.delete(1.0, tk.END)
        self.matrix1_text.insert(1.0, self._format_matrix_display(identity))
        self._update_status(f"Generated {size}x{size} identity matrix")
    
    def _format_matrix_display(self, matrix):
        """Format matrix for display"""
        if isinstance(matrix, list):
            matrix = np.array(matrix)
        return np.array2string(matrix, precision=3, suppress_small=True, separator=', ')
    
    def _execute_operation(self):
        """Execute the selected matrix operation"""
        if self.waiting_for_response:
            messagebox.showwarning("Operation in Progress", "Please wait for current operation to complete")
            return
        
        try:
            operation = OperationType(self.operation_var.get())
            matrices = []
            scalar = None
            
            # Parse matrices from text areas
            matrix1_str = self.matrix1_text.get(1.0, tk.END).strip()
            if matrix1_str:
                matrix1 = self._parse_matrix_from_text(matrix1_str)
                matrices.append(matrix1)
            
            # Check if operation needs second matrix
            if operation in [OperationType.ADD, OperationType.SUBTRACT, OperationType.MULTIPLY]:
                matrix2_str = self.matrix2_text.get(1.0, tk.END).strip()
                if matrix2_str:
                    matrix2 = self._parse_matrix_from_text(matrix2_str)
                    matrices.append(matrix2)
                else:
                    messagebox.showerror("Error", f"{operation.value} requires two matrices")
                    return
            
            # Check if operation needs scalar
            if operation == OperationType.SCALAR_MULTIPLY:
                try:
                    scalar = float(self.scalar_var.get())
                except ValueError:
                    messagebox.showerror("Error", "Invalid scalar value")
                    return
            
            # Send operation to server
            self._send_operation(operation, matrices, scalar)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error executing operation: {e}")
            self._update_status(f"Error: {e}")
    
    def _parse_matrix_from_text(self, text: str) -> List[List[float]]:
        """Parse matrix from text representation"""
        try:
            # Try to evaluate as numpy array string first
            if text.startswith('[') and text.endswith(']'):
                # Handle numpy array string format
                matrix_str = text.replace('\n', ' ')
                matrix = eval(matrix_str)
                if isinstance(matrix, (list, np.ndarray)):
                    return np.array(matrix).tolist()
            
            # Try line-by-line parsing
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            matrix = []
            for line in lines:
                # Remove brackets and split by comma or whitespace
                line = line.strip('[]')
                row = [float(x) for x in line.replace(',', ' ').split()]
                matrix.append(row)
            
            return matrix
            
        except Exception as e:
            raise ValueError(f"Could not parse matrix: {e}")
    
    def _send_operation(self, operation: OperationType, matrices: List, scalar: Optional[float]):
        """Send operation to server"""
        try:
            # Create payload
            payload = create_matrix_operation_payload(operation, matrices, scalar)
            
            # Encrypt payload
            encrypted_payload = self.encryption.encrypt_packet_payload(payload)
            
            # Create packet
            packet = self.reliability.create_packet(PacketType.MATRIX_OP, encrypted_payload)
            self.reliability.add_pending_ack(packet)
            
            # Send to server
            server_addr = (self.server_host, self.server_port)
            self.socket.sendto(packet.to_bytes(), server_addr)
            
            self.waiting_for_response = True
            self.current_operation = operation
            self._update_status(f"Sent {operation.value} operation to server...")
            
            # Start response listener
            threading.Thread(target=self._wait_for_response, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Network Error", f"Failed to send operation: {e}")
            self._update_status(f"Send error: {e}")
    
    def _wait_for_response(self):
        """Wait for server response"""
        start_time = time.time()
        timeout = 10.0  # 10 second timeout
        
        while self.waiting_for_response and (time.time() - start_time) < timeout:
            try:
                data, server_addr = self.socket.recvfrom(65536)
                
                # Parse response packet
                packet = Packet.from_bytes(data)
                
                if packet.packet_type in [PacketType.RESULT, PacketType.ERROR]:
                    # Decrypt result
                    decrypted_payload = self.encryption.decrypt_packet_payload(packet.payload)
                    success, result, error_message = parse_result_payload(decrypted_payload)
                    
                    # Update GUI on main thread
                    self.root.after(0, self._handle_response, success, result, error_message)
                    break
                    
            except socket.timeout:
                continue
            except Exception as e:
                self.root.after(0, self._handle_response, False, None, f"Response error: {e}")
                break
        
        if self.waiting_for_response:
            # Timeout occurred
            self.root.after(0, self._handle_response, False, None, "Operation timed out")
    
    def _handle_response(self, success: bool, result, error_message: Optional[str]):
        """Handle server response on main thread"""
        self.waiting_for_response = False
        
        if success and result is not None:
            # Display result
            if isinstance(result, (int, float)):
                result_str = f"Result: {result}"
            else:
                result_matrix = np.array(result)
                result_str = f"Result ({result_matrix.shape}):\n{self._format_matrix_display(result_matrix)}"
            
            self.result_text.insert(tk.END, f"\n{self.current_operation.value.upper()} OPERATION:\n")
            self.result_text.insert(tk.END, f"{result_str}\n")
            self.result_text.insert(tk.END, "-" * 50 + "\n")
            self.result_text.see(tk.END)
            
            self._update_status(f"{self.current_operation.value} completed successfully")
        else:
            error_msg = error_message or "Unknown error"
            self.result_text.insert(tk.END, f"\nERROR in {self.current_operation.value}:\n{error_msg}\n")
            self.result_text.insert(tk.END, "-" * 50 + "\n")
            self.result_text.see(tk.END)
            
            self._update_status(f"Operation failed: {error_msg}")
    
    def _clear_results(self):
        """Clear the results area"""
        self.result_text.delete(1.0, tk.END)
        self._update_status("Results cleared")
    
    def _update_status(self, message: str):
        """Update status bar"""
        if self.status_label:
            self.status_label.config(text=message)

class MatrixEntryDialog:
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manual Matrix Entry")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        ttk.Label(self.dialog, text="Enter matrix (one row per line, space-separated values):").pack(pady=10)
        
        self.text_area = scrolledtext.ScrolledText(self.dialog, height=12, width=50)
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Sample text
        sample_matrix = "1.0 2.0 3.0\n4.0 5.0 6.0\n7.0 8.0 9.0"
        self.text_area.insert(tk.END, sample_matrix)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to complete
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        """Handle OK button"""
        try:
            text = self.text_area.get(1.0, tk.END).strip()
            matrix = []
            
            for line in text.split('\n'):
                if line.strip():
                    row = [float(x) for x in line.strip().split()]
                    matrix.append(row)
            
            if matrix:
                self.result = matrix
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid matrix format: {e}")
    
    def _cancel_clicked(self):
        """Handle Cancel button"""
        self.dialog.destroy()

def main():
    """Main client entry point"""
    client = MatrixClient()
    client.start_gui()

if __name__ == "__main__":
    main()