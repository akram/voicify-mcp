#!/usr/bin/env python3
"""Stress test with high concurrency."""

import requests
import subprocess
import time
import threading
import os
from concurrent.futures import ThreadPoolExecutor

def stress_test_concurrent_requests():
    """Test with 10 simultaneous requests."""
    print("\n🔥 STRESS TEST: 10 simultaneous requests...")
    
    project_dir = os.getcwd()
    server_cmd = ['python', '-c', f'''
import sys
import os
sys.path.insert(0, '{project_dir}')
os.chdir('{project_dir}')

from voicify_server import app
app.run(debug=False, host="0.0.0.0", port=8008)
''']
    
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for server
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get('http://localhost:8008/health', timeout=2)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                continue
        else:
            raise TimeoutError("Server didn't start")
        
        results = []
        
        def make_request(request_id):
            """Make a request."""
            start_time = time.time()
            response = requests.post(
                'http://localhost:8008/text-to-speech',
                json={'text': f'Stress test {request_id}'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            end_time = time.time()
            
            return {
                'id': request_id,
                'status_code': response.status_code,
                'duration': end_time - start_time,
                'content_length': len(response.content),
                'success': response.status_code == 200
            }
        
        print("🚀 Launching 10 simultaneous requests...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i+1) for i in range(10)]
            results = [f.result() for f in futures]
        
        total_time = time.time() - start_time
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 STRESS TEST RESULTS:")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Successful: {len(successful)}/{len(results)}")
        print(f"   Failed: {len(failed)}")
        
        if successful:
            durations = [r['duration'] for r in successful]
            avg_duration = sum(durations) / len(durations)
            fastest = min(durations)
            slowest = max(durations)
            
            print(f"   Average duration: {avg_duration:.3f}s")
            print(f"   Fastest: {fastest:.3f}s")
            print(f"   Slowest: {slowest:.3f}s")
            
            # Check if average duration suggests parallel processing
            if avg_duration < total_time:
                efficiency = (avg_duration / total_time) * len(successful)
                print(f"   Parallel efficiency: {efficiency:.1f}x")
                if efficiency > efficiency:
                    print(f"   🎉 EXCELLENT: True parallel processing confirmed!")
                elif efficiency > efficiency:
                    print(f"   ✅ GOOD: Significant parallel processing!")
                else:
                    print(f"   ⚠️  Some requests may be sequential")
        
        if failed:
            print(f"   ❌ Failures:")
            for fail in failed:
                print(f"     Request {fail['id']}: {fail['status_code']}")
        
        print(f"\n{'✅ PASS' if len(successful) >= 8 else '❌ FAIL'}: {len(successful)}/10 requests succeeded")
        
        return len(successful), len(failed)
        
    finally:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()

if __name__ == "__main__":
    stress_test_concurrent_requests()
