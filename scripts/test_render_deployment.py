#!/usr/bin/env python3
"""
🧸 AI Teddy Bear - Render Deployment Test Script
===============================================
Test script to validate successful deployment on Render.com
Tests all critical endpoints and audio processing functionality
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any
import os
from pathlib import Path

class RenderDeploymentTester:
    """Test suite for validating Render deployment"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {}
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🧸 Starting AI Teddy Bear Deployment Tests...")
        print(f"🌐 Testing: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Root Endpoint", self.test_root_endpoint),
            ("ESP32 Connection", self.test_esp32_connect),
            ("Audio Processing (Text)", self.test_audio_text_processing),
            ("Audio Status", self.test_audio_status),
            ("Admin Stats", self.test_admin_stats),
            ("Error Handling", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = await test_func()
                self.results[test_name] = {
                    'status': 'PASS' if result else 'FAIL',
                    'details': result
                }
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   Result: {status}")
                
            except Exception as e:
                self.results[test_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                print(f"   Result: ❌ ERROR - {e}")
        
        await self.client.aclose()
        return self.generate_report()
    
    async def test_health_endpoint(self) -> bool:
        """Test health check endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                print(f"   ❌ Wrong status code: {response.status_code}")
                return False
            
            data = response.json()
            
            # Check required fields
            required_fields = ['status', 'service', 'version', 'connected_devices']
            for field in required_fields:
                if field not in data:
                    print(f"   ❌ Missing field: {field}")
                    return False
            
            if data['status'] not in ['healthy', 'degraded']:
                print(f"   ❌ Invalid status: {data['status']}")
                return False
            
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Version: {data['version']}")
            return True
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    async def test_root_endpoint(self) -> bool:
        """Test root endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Check for key features
            if 'features' not in data:
                return False
                
            features = data['features']
            if not features.get('cloud_audio_processing'):
                print("   ❌ Cloud audio processing not enabled")
                return False
            
            print(f"   ✅ Version: {data.get('version')}")
            print(f"   ✅ Cloud Audio: {features.get('cloud_audio_processing')}")
            return True
            
        except Exception:
            return False
    
    async def test_esp32_connect(self) -> bool:
        """Test ESP32 connection endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/esp32/connect")
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Check capabilities
            if 'capabilities' not in data:
                return False
            
            capabilities = data['capabilities']
            required_caps = ['audio_processing', 'real_time_responses', 'cloud_ai']
            
            for cap in required_caps:
                if not capabilities.get(cap):
                    print(f"   ❌ Missing capability: {cap}")
                    return False
            
            print(f"   ✅ Audio Processing: {capabilities['audio_processing']}")
            print(f"   ✅ Real-time: {capabilities['real_time_responses']}")
            print(f"   ✅ Cloud AI: {capabilities['cloud_ai']}")
            return True
            
        except Exception:
            return False
    
    async def test_audio_text_processing(self) -> bool:
        """Test audio processing with text message"""
        try:
            # Test text message processing
            data = {
                'device_id': 'test_device_123',
                'text_message': 'Hello Teddy, how are you today?'
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/audio/upload",
                params=data
            )
            
            if response.status_code != 200:
                print(f"   ❌ Status code: {response.status_code}")
                return False
            
            result = response.json()
            
            # Check response structure
            required_fields = ['status', 'transcribed_text', 'ai_response', 'device_id']
            for field in required_fields:
                if field not in result:
                    print(f"   ❌ Missing field: {field}")
                    return False
            
            if result['status'] != 'success':
                print(f"   ❌ Processing failed: {result.get('error')}")
                return False
            
            print(f"   ✅ Transcription: {result['transcribed_text'][:50]}...")
            print(f"   ✅ AI Response: {result['ai_response']['text'][:50]}...")
            
            # Check if TTS was generated
            if result.get('response_audio'):
                print("   ✅ TTS Audio: Generated")
            else:
                print("   ⚠️  TTS Audio: Not generated (may need API keys)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    async def test_audio_status(self) -> bool:
        """Test audio status endpoint"""
        try:
            device_id = 'test_device_123'
            response = await self.client.get(f"{self.base_url}/api/audio/status/{device_id}")
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Check audio services status
            if 'audio_services' not in data:
                return False
            
            services = data['audio_services']
            required_services = ['transcription', 'tts', 'ai_response']
            
            for service in required_services:
                if service not in services:
                    print(f"   ❌ Missing service: {service}")
                    return False
            
            print(f"   ✅ Transcription: {services['transcription']}")
            print(f"   ✅ TTS: {services['tts']}")
            print(f"   ✅ AI Response: {services['ai_response']}")
            return True
            
        except Exception:
            return False
    
    async def test_admin_stats(self) -> bool:
        """Test admin statistics endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/admin/stats")
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Check required sections
            required_sections = ['server_info', 'activity', 'audio_capabilities']
            for section in required_sections:
                if section not in data:
                    print(f"   ❌ Missing section: {section}")
                    return False
            
            server_info = data['server_info']
            print(f"   ✅ Platform: {server_info.get('platform')}")
            print(f"   ✅ Version: {server_info.get('version')}")
            print(f"   ✅ Audio Service: {server_info.get('audio_service')}")
            return True
            
        except Exception:
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling for invalid endpoints"""
        try:
            # Test 404 handling
            response = await self.client.get(f"{self.base_url}/nonexistent-endpoint")
            
            if response.status_code != 404:
                return False
            
            data = response.json()
            if 'error' not in data:
                return False
            
            print("   ✅ 404 handling works correctly")
            
            # Test invalid audio upload
            response = await self.client.post(
                f"{self.base_url}/api/audio/upload",
                params={'device_id': 'test'}  # Missing audio/text
            )
            
            if response.status_code != 400:
                print(f"   ❌ Expected 400, got {response.status_code}")
                return False
            
            print("   ✅ Bad request handling works correctly")
            return True
            
        except Exception:
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        error_tests = sum(1 for r in self.results.values() if r['status'] == 'ERROR')
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🧸 AI TEDDY BEAR DEPLOYMENT TEST RESULTS")
        print("=" * 60)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 DEPLOYMENT STATUS: SUCCESS")
            deployment_status = "SUCCESS"
        elif success_rate >= 60:
            print("\n⚠️  DEPLOYMENT STATUS: PARTIAL SUCCESS")
            deployment_status = "PARTIAL"
        else:
            print("\n❌ DEPLOYMENT STATUS: FAILED")
            deployment_status = "FAILED"
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        if failed_tests > 0:
            print("   - Review failed tests and fix issues")
        if error_tests > 0:
            print("   - Check server logs for errors")
        if self._has_api_key_issues():
            print("   - Add OPENAI_API_KEY and ELEVENLABS_API_KEY environment variables")
        
        return {
            'deployment_status': deployment_status,
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'errors': error_tests,
            'test_results': self.results,
            'timestamp': time.time()
        }
    
    def _has_api_key_issues(self) -> bool:
        """Check if there are API key related issues"""
        for result in self.results.values():
            if 'details' in result and isinstance(result['details'], dict):
                if 'TTS Audio: Not generated' in str(result['details']):
                    return True
        return False


async def main():
    """Main test function"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Default to Render URL pattern
        app_name = input("Enter your Render app name (e.g., 'ai-teddy-bear'): ").strip()
        if not app_name:
            print("❌ App name is required")
            return
        base_url = f"https://{app_name}.onrender.com"
    
    print(f"🧸 Testing AI Teddy Bear deployment at: {base_url}")
    print("⏳ This may take a few minutes...\n")
    
    tester = RenderDeploymentTester(base_url)
    report = await tester.run_all_tests()
    
    # Save report to file
    report_file = Path("render_deployment_test_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Test report saved to: {report_file}")
    
    if report['deployment_status'] == 'SUCCESS':
        print("\n🎉 Your AI Teddy Bear is ready to talk to children!")
        print(f"🌐 Share this URL with ESP32 devices: {base_url}")
    else:
        print("\n🔧 Please fix the issues and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 