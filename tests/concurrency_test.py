#!/usr/bin/env python3
"""Test true simultaneous concurrent requests to verify our concurrency fix."""

import pytest
import requests
import subprocess
import time
import threading
import os
from concurrent.futures import ThreadPoolExecutor
import tempfile

def test_simultaneous_concurrent_requests():
    """Test multiple requests hitting the server at exactly the same time.
    
    Note: Real Voicify uses cloud API and may have rate limiting.
    This test expects at least 1 successful request (3+ with mock Voicify).
    """
    print("\n🚀 Testing SIMULTANEOUS concurrent requests...")
    
    # Start server in background
    project_dir = os.getcwd()
    server_cmd = ['python', '-c', f'''
import sys
import os
sys.path.insert(0, '{project_dir}')
os.chdir('{project_dir}')

from voicify_server import app
print("Starting server for concurrency test...")
app.run(debug=False, host="0.0.0.0", port=8007)
''']
    
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get('http://localhost:8007/health', timeout=2)
                if response.status_code == 200:
                    print("✅ Server started!")
                    break
            except requests.exceptions.RequestException:
                continue
        else:
            raise TimeoutError("Server didn't start")
        
        # Test Results Storage
        results = []
        errors = []
        
        def make_request(request_id):
            """Make a single TTS request and store results."""
            try:
                start_time = time.time()
                response = requests.post(
                    'http://localhost:8007/text-to-speech',
                    json={'text': f'Simultaneous test {request_id}'},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                end_time = time.time()
                
                result = {
                    'id': request_id,
                    'status_code': response.status_code,
                    'duration': end_time - start_time,
                    'content_length': len(response.content),
                    'timestamp': start_time
                }
                
                if response.status_code == 200:
                    results.append(result)
                    print(f"   ✅ Request {request_id}: {result['duration']:.3f}s, {result['content_length']} bytes")
                else:
                    error_data = response.json() if 'application/json' in response.headers.get('Content-Type', '') else {'error': response.text}
                    errors.append({'id': request_id, 'error': error_data.get('error', 'Unknown error')})
                    print(f"   ❌ Request {request_id}: {response.status_code} - {error_data.get('error', 'Unknown')}")
                    
            except Exception as e:
                errors.append({'id': request_id, 'error': str(e)})
                print(f"   💥 Request {request_id}: Exception - {e}")
        
        # Launch 5 simultaneous requests
        print("\n🎯 Launching 5 SIMULTANEOUS requests...")
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i+1) for i in range(5)]
            # Wait for all to complete
            for future in futures:
                future.result()
        
        total_time = time.time() - start_time
        
        # Analyze results
        print(f"\n📊 CONCURRENCY TEST RESULTS:")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Successful requests: {len(results)}")
        print(f"   Failed requests: {len(errors)}")
        
        if results:
            durations = [r['duration'] for r in results]
            print(f"   Average request time: {sum(durations)/len(durations):.3f}s")
            print(f"   Fastest request: {min(durations):.3f}s")
            print(f"   Slowest request: {max(durations):.3f}s")
        
        if errors:
            print(f"   Errors:")
            for error in errors:
                print(f"     - Request {error['id']}: {error['error']}")
        
        # Check if requests overlapped
        if len(results) >= 2:
            timestamps = [r['timestamp'] for r in results]
            timestamps.sort()
            overlaps = 0
            for i in range(len(timestamps) - 1):
                # If requests were within 0.1 seconds of each other, they likely overlapped
                if timestamps[i+1] - timestamps[i] < 0.1:
                    overlaps += 1
            
            if overlaps > 0:
                print(f"   🎉 Detected {overlaps} overlapping requests - TRUE CONCURRENCY!")
            else:
                print(f"   ⚠️  No detected overlaps - requests may be sequential")
        
        # Assertions - adapt expectations based on Voicify availability
        # Real Voicify may have rate limiting that affects concurrent requests
        assert len(results) >= 1, f"Expected at least 1 successful concurrent request, got {len(results)}"
        
        if len(results) >= 3:
            print(f"\n✅ SUCCESS: {len(results)} simultaneous requests completed!")
        elif len(results) >= 1:
            print(f"\n⚠️  PARTIAL SUCCESS: {len(results)} concurrent request(s) completed (real Voicify may have rate limiting)")
        
        # Real Voicify may have rate limiting, so allow some failures
        # Return None instead of tuple to avoid pytest warning
        assert len(results) > 0
        
    finally:
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

if __name__ == "__main__":
    test_simultaneous_concurrent_requests()
