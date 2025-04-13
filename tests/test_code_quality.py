"""
Test file for running Vulture to find dead code.
"""
import os
import sys
import subprocess
from pathlib import Path
import pytest

def run_vulture():
    """Run Vulture to find dead code in the project."""
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Find the Python interpreter in the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = str(root_dir / ".venv" / "Scripts" / "python.exe")
    else:  # Unix/Linux/Mac
        python_executable = str(root_dir / ".venv" / "bin" / "python")
    
    # Set up the command to run vulture on the project
    cmd = [python_executable, "-m", "vulture", 
           str(root_dir / "data_analysis"),
           str(root_dir / "scripts"),
           str(root_dir / "utils"),
           "--exclude", "*/__pycache__/*,*/\\.venv/*,*/tests/*",
           "--min-confidence", "80"]
    
    # Run the command
    print("Running Vulture to find dead code...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output
    print("\nVulture Output:")
    print(result.stdout or "No dead code found!")
    
    if result.stderr:
        print("\nErrors:")
        print(result.stderr)
    
    # Return success if no dead code was found
    return not bool(result.stdout)

def run_mypy():
    """Run Mypy for type checking."""
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Find the Python interpreter in the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = str(root_dir / ".venv" / "Scripts" / "python.exe")
    else:  # Unix/Linux/Mac
        python_executable = str(root_dir / ".venv" / "bin" / "python")
    
    # Set up the command to run mypy on the project
    cmd = [python_executable, "-m", "mypy",
           str(root_dir / "data_analysis"),
           str(root_dir / "scripts"),
           str(root_dir / "utils"),
           "--ignore-missing-imports"]
    
    # Run the command
    print("\nRunning Mypy for type checking...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output
    print("\nMypy Output:")
    if not result.stdout:
        print("No type errors found!")
    else:
        print(result.stdout)
    
    if result.stderr:
        print("\nErrors:")
        print(result.stderr)
    
    # Return success if no type errors were found (exit code 0)
    return result.returncode == 0

def main():
    """Run all code quality checks."""
    vulture_success = run_vulture()
    mypy_success = run_mypy()
    
    if vulture_success and mypy_success:
        print("\nAll code quality checks passed!")
        return 0
    else:
        print("\nSome code quality checks failed.")
        return 1

def test_vulture():
    """Test that there is no dead code in the project using Vulture."""
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Find the Python interpreter in the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = str(root_dir / ".venv" / "Scripts" / "python.exe")
    else:  # Unix/Linux/Mac
        python_executable = str(root_dir / ".venv" / "bin" / "python")
    
    # Set up the command to run vulture on the project
    cmd = [python_executable, "-m", "vulture", 
           str(root_dir / "data_analysis"),
           str(root_dir / "scripts"),
           str(root_dir / "utils"),
           "--exclude", "*/__pycache__/*,*/\\.venv/*,*/tests/*",
           "--min-confidence", "80"]
    
    # Run the command
    print("\nRunning Vulture to find dead code...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output for visibility
    if result.stdout:
        print("\nPotential dead code found:")
        print(result.stdout)
    
    # Assert that no dead code was found
    assert not result.stdout, "Dead code found by Vulture"

def test_mypy():
    """Test that there are no type errors using Mypy."""
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Find the Python interpreter in the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = str(root_dir / ".venv" / "Scripts" / "python.exe")
    else:  # Unix/Linux/Mac
        python_executable = str(root_dir / ".venv" / "bin" / "python")
    
    # Set up the command to run mypy on the project
    cmd = [python_executable, "-m", "mypy",
           str(root_dir / "data_analysis"),
           str(root_dir / "scripts"),
           str(root_dir / "utils"),
           "--ignore-missing-imports"]
    
    # Run the command
    print("\nRunning Mypy for type checking...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output for visibility
    if result.stdout:
        print("\nType issues found:")
        print(result.stdout)
    
    # Assert that mypy ran successfully
    assert result.returncode == 0, "Type errors found by Mypy"

if __name__ == "__main__":
    sys.exit(main())