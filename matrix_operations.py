import numpy as np
from typing import Union, List, Tuple, Any, Optional
from protocol import OperationType

class MatrixProcessor:
    """Handles all linear algebra operations"""
    
    @staticmethod
    def add_matrices(matrix1: List[List[float]], matrix2: List[List[float]]) -> np.ndarray:
        """Add two matrices"""
        m1 = np.array(matrix1)
        m2 = np.array(matrix2)
        if m1.shape != m2.shape:
            raise ValueError(f"Matrix dimensions don't match: {m1.shape} vs {m2.shape}")
        return m1 + m2
    
    @staticmethod
    def subtract_matrices(matrix1: List[List[float]], matrix2: List[List[float]]) -> np.ndarray:
        """Subtract two matrices"""
        m1 = np.array(matrix1)
        m2 = np.array(matrix2)
        if m1.shape != m2.shape:
            raise ValueError(f"Matrix dimensions don't match: {m1.shape} vs {m2.shape}")
        return m1 - m2
    
    @staticmethod
    def multiply_matrices(matrix1: List[List[float]], matrix2: List[List[float]]) -> np.ndarray:
        """Multiply two matrices"""
        m1 = np.array(matrix1)
        m2 = np.array(matrix2)
        if m1.shape[1] != m2.shape[0]:
            raise ValueError(f"Cannot multiply matrices: {m1.shape} and {m2.shape}")
        return np.matmul(m1, m2)
    
    @staticmethod
    def scalar_multiply(matrix: List[List[float]], scalar: float) -> np.ndarray:
        """Multiply matrix by scalar"""
        m = np.array(matrix)
        return m * scalar
    
    @staticmethod
    def transpose_matrix(matrix: List[List[float]]) -> np.ndarray:
        """Transpose matrix"""
        m = np.array(matrix)
        return m.T
    
    @staticmethod
    def inverse_matrix(matrix: List[List[float]]) -> np.ndarray:
        """Calculate matrix inverse"""
        m = np.array(matrix)
        if m.shape[0] != m.shape[1]:
            raise ValueError("Matrix must be square for inverse")
        det = np.linalg.det(m)
        if abs(det) < 1e-10:
            raise ValueError("Matrix is singular (not invertible)")
        return np.linalg.inv(m)
    
    @staticmethod
    def determinant(matrix: List[List[float]]) -> float:
        """Calculate matrix determinant"""
        m = np.array(matrix)
        if m.shape[0] != m.shape[1]:
            raise ValueError("Matrix must be square for determinant")
        return float(np.linalg.det(m))
    
    @staticmethod
    def rank(matrix: List[List[float]]) -> int:
        """Calculate matrix rank"""
        m = np.array(matrix)
        return int(np.linalg.matrix_rank(m))
    
    @classmethod
    def process_operation(cls, operation: OperationType, matrices: List[List[List[float]]], scalar: Optional[float] = None) -> Any:
        """Process a matrix operation based on operation type"""
        try:
            if operation == OperationType.ADD:
                if len(matrices) != 2:
                    raise ValueError("Addition requires exactly 2 matrices")
                return cls.add_matrices(matrices[0], matrices[1])
            
            elif operation == OperationType.SUBTRACT:
                if len(matrices) != 2:
                    raise ValueError("Subtraction requires exactly 2 matrices")
                return cls.subtract_matrices(matrices[0], matrices[1])
            
            elif operation == OperationType.MULTIPLY:
                if len(matrices) != 2:
                    raise ValueError("Multiplication requires exactly 2 matrices")
                return cls.multiply_matrices(matrices[0], matrices[1])
            
            elif operation == OperationType.SCALAR_MULTIPLY:
                if len(matrices) != 1 or scalar is None:
                    raise ValueError("Scalar multiplication requires 1 matrix and a scalar value")
                return cls.scalar_multiply(matrices[0], scalar)
            
            elif operation == OperationType.TRANSPOSE:
                if len(matrices) != 1:
                    raise ValueError("Transpose requires exactly 1 matrix")
                return cls.transpose_matrix(matrices[0])
            
            elif operation == OperationType.INVERSE:
                if len(matrices) != 1:
                    raise ValueError("Inverse requires exactly 1 matrix")
                return cls.inverse_matrix(matrices[0])
            
            elif operation == OperationType.DETERMINANT:
                if len(matrices) != 1:
                    raise ValueError("Determinant requires exactly 1 matrix")
                return cls.determinant(matrices[0])
            
            elif operation == OperationType.RANK:
                if len(matrices) != 1:
                    raise ValueError("Rank requires exactly 1 matrix")
                return cls.rank(matrices[0])
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        
        except Exception as e:
            raise ValueError(f"Error processing {operation.value}: {str(e)}")

def generate_random_matrix(rows: int, cols: int, min_val: float = -10.0, max_val: float = 10.0) -> List[List[float]]:
    """Generate a random matrix for testing"""
    matrix = np.random.uniform(min_val, max_val, (rows, cols))
    return matrix.tolist()

def create_identity_matrix(size: int) -> List[List[float]]:
    """Create an identity matrix"""
    return np.eye(size).tolist()

def create_zero_matrix(rows: int, cols: int) -> List[List[float]]:
    """Create a zero matrix"""
    return np.zeros((rows, cols)).tolist()