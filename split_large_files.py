#!/usr/bin/env python3
"""
File splitter for large Python files.
Splits files into chunks of max 200 lines or 10KB while preserving syntax.
"""

import os
import ast
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Tuple


class PythonFileSplitter:
    def __init__(self, max_lines: int = 200, max_size_kb: int = 10):
        self.max_lines = max_lines
        self.max_size_kb = max_size_kb * 1024  # Convert to bytes
        
    def extract_header_and_imports(self, content: str) -> Tuple[str, int]:
        """Extract file header and imports section."""
        lines = content.split('\n')
        header_lines = []
        import_section_end = 0
        
        # Find the end of imports and module-level docstrings
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Keep comments, docstrings, and imports
            if (stripped.startswith('#') or 
                stripped.startswith('"""') or 
                stripped.startswith("'''") or
                stripped.startswith('import ') or
                stripped.startswith('from ') or
                line.startswith('try:') or
                line.startswith('except ImportError:') or
                stripped == '' or
                'import' in stripped):
                header_lines.append(line)
                import_section_end = i + 1
            elif stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('@'):
                break
            else:
                # Check if this is still part of import section
                if any(keyword in stripped for keyword in ['import', 'from']):
                    header_lines.append(line)
                    import_section_end = i + 1
                elif not stripped:  # Empty line
                    header_lines.append(line)
                    import_section_end = i + 1
                else:
                    break
        
        return '\n'.join(header_lines), import_section_end
    
    def find_class_function_boundaries(self, content: str, start_line: int = 0) -> List[Tuple[int, int, str]]:
        """Find boundaries of classes and functions."""
        lines = content.split('\n')
        boundaries = []
        current_indent = 0
        current_start = start_line
        current_name = "module_start"
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                continue
                
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            
            # Check for class or function definition
            if stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('@'):
                # Save previous boundary
                if i > current_start:
                    boundaries.append((current_start, i - 1, current_name))
                
                # Extract name
                if stripped.startswith('class '):
                    current_name = stripped.split('class ')[1].split('(')[0].split(':')[0].strip()
                elif stripped.startswith('def '):
                    current_name = stripped.split('def ')[1].split('(')[0].strip()
                elif stripped.startswith('@'):
                    current_name = f"decorator_{i}"
                
                current_start = i
                current_indent = indent
            
            # Check if we're at the end of a class/function (when indentation returns to 0 or decreases significantly)
            elif indent <= current_indent and current_start < i and not stripped.startswith(('class ', 'def ', '@')):
                if stripped:  # Only if it's not an empty line
                    boundaries.append((current_start, i - 1, current_name))
                    current_start = i
                    current_name = f"module_section_{i}"
                    current_indent = 0
        
        # Add final boundary
        if current_start < len(lines):
            boundaries.append((current_start, len(lines) - 1, current_name))
        
        return boundaries
    
    def validate_python_syntax(self, content: str) -> bool:
        """Validate Python syntax."""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def calculate_md5(self, content: str) -> str:
        """Calculate MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def split_file(self, file_path: str) -> Dict:
        """Split a large Python file into smaller chunks."""
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Extract header and imports
        header, import_end = self.extract_header_and_imports(original_content)
        
        # Find class/function boundaries
        boundaries = self.find_class_function_boundaries(original_content, import_end)
        
        # Group boundaries into chunks
        chunks = []
        current_chunk_lines = []
        current_chunk_size = len(header.encode('utf-8'))
        chunk_start_line = 0
        
        lines = original_content.split('\n')
        
        for start_line, end_line, name in boundaries:
            # Get the content for this boundary
            boundary_lines = lines[start_line:end_line + 1]
            boundary_content = '\n'.join(boundary_lines)
            boundary_size = len(boundary_content.encode('utf-8'))
            
            # Check if adding this boundary would exceed limits
            if (len(current_chunk_lines) + len(boundary_lines) > self.max_lines or
                current_chunk_size + boundary_size > self.max_size_kb):
                
                # Save current chunk if it has content
                if current_chunk_lines:
                    chunk_content = header + '\n\n' + '\n'.join(current_chunk_lines)
                    chunks.append({
                        'content': chunk_content,
                        'start_line': chunk_start_line,
                        'end_line': start_line - 1,
                        'line_count': len(chunk_content.split('\n')),
                        'size_bytes': len(chunk_content.encode('utf-8'))
                    })
                
                # Start new chunk
                current_chunk_lines = boundary_lines
                current_chunk_size = len(header.encode('utf-8')) + boundary_size
                chunk_start_line = start_line
            else:
                # Add to current chunk
                current_chunk_lines.extend(boundary_lines)
                current_chunk_size += boundary_size
        
        # Add final chunk
        if current_chunk_lines:
            chunk_content = header + '\n\n' + '\n'.join(current_chunk_lines)
            chunks.append({
                'content': chunk_content,
                'start_line': chunk_start_line,
                'end_line': len(lines) - 1,
                'line_count': len(chunk_content.split('\n')),
                'size_bytes': len(chunk_content.encode('utf-8'))
            })
        
        # Create split files
        base_name = Path(file_path).stem
        directory = Path(file_path).parent
        
        split_files = []
        for i, chunk in enumerate(chunks, 1):
            chunk_filename = f"{base_name}_part{i}.py"
            chunk_path = directory / chunk_filename
            
            # Validate syntax
            if not self.validate_python_syntax(chunk['content']):
                print(f"WARNING: Syntax error in chunk {i} of {file_path}")
            
            # Write chunk file
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk['content'])
            
            split_files.append({
                'filename': chunk_filename,
                'path': str(chunk_path),
                'lines': chunk['line_count'],
                'size_bytes': chunk['size_bytes'],
                'size_kb': round(chunk['size_bytes'] / 1024, 2),
                'checksum': self.calculate_md5(chunk['content']),
                'syntax_valid': self.validate_python_syntax(chunk['content'])
            })
        
        # Create manifest
        manifest = {
            'original_file': file_path,
            'original_lines': len(original_content.split('\n')),
            'original_size_bytes': len(original_content.encode('utf-8')),
            'original_checksum': self.calculate_md5(original_content),
            'chunks_created': len(split_files),
            'split_files': split_files,
            'split_timestamp': Path(file_path).stat().st_mtime,
            'validation': {
                'total_lines_match': sum(f['lines'] for f in split_files) >= len(original_content.split('\n')),
                'all_syntax_valid': all(f['syntax_valid'] for f in split_files)
            }
        }
        
        # Save manifest
        manifest_path = directory / f"{base_name}_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest


def main():
    """Main function to split the large files."""
    files_to_split = [
        "src/application/services/ai/llm_service_factory.py",
        "src/adapters/edge/edge_ai_manager.py", 
        "src/application/services/ai/main_service.py",
        "src/application/services/core/moderation_service.py"
    ]
    
    splitter = PythonFileSplitter(max_lines=200, max_size_kb=10)
    results = {}
    
    for file_path in files_to_split:
        if os.path.exists(file_path):
            print(f"Splitting {file_path}...")
            try:
                manifest = splitter.split_file(file_path)
                results[file_path] = manifest
                print(f"  ✓ Created {manifest['chunks_created']} chunks")
                print(f"  ✓ All syntax valid: {manifest['validation']['all_syntax_valid']}")
            except Exception as e:
                print(f"  ✗ Error splitting {file_path}: {e}")
                results[file_path] = {"error": str(e)}
        else:
            print(f"  ✗ File not found: {file_path}")
            results[file_path] = {"error": "File not found"}
    
    # Create summary report
    summary = {
        'total_files_processed': len(files_to_split),
        'successful_splits': len([r for r in results.values() if 'chunks_created' in r]),
        'total_chunks_created': sum(r.get('chunks_created', 0) for r in results.values()),
        'files': results
    }
    
    with open('file_splitting_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {summary['total_files_processed']}")
    print(f"Successful splits: {summary['successful_splits']}")
    print(f"Total chunks created: {summary['total_chunks_created']}")
    print(f"Summary saved to: file_splitting_summary.json")


if __name__ == "__main__":
    main() 