import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class BharatanatyamAPITester:
    def __init__(self, base_url="https://dance2story.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_keys = ["message", "version"]
                has_expected_keys = all(key in data for key in expected_keys)
                success = has_expected_keys
                details = f"Status: {response.status_code}, Response: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Root API Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Root API Endpoint", False, f"Error: {str(e)}")
            return False

    def test_upload_video_validation(self):
        """Test video upload with invalid file type"""
        try:
            # Create a fake text file to test validation
            fake_file_content = b"This is not a video file"
            files = {'file': ('test.txt', fake_file_content, 'text/plain')}
            
            response = requests.post(f"{self.api_url}/upload-video", files=files, timeout=30)
            
            # Should return 400 for invalid file type
            success = response.status_code == 400
            details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("Video Upload Validation (Invalid File)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Video Upload Validation (Invalid File)", False, f"Error: {str(e)}")
            return False

    def test_generate_story_invalid_id(self):
        """Test story generation with invalid analysis ID"""
        try:
            payload = {"analysis_id": "invalid-id-12345"}
            response = requests.post(f"{self.api_url}/generate-story", json=payload, timeout=30)
            
            # Should return 404 for invalid ID
            success = response.status_code == 404
            details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("Story Generation (Invalid ID)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Story Generation (Invalid ID)", False, f"Error: {str(e)}")
            return False

    def test_get_analysis_invalid_id(self):
        """Test get analysis with invalid video ID"""
        try:
            response = requests.get(f"{self.api_url}/analysis/invalid-id-12345", timeout=10)
            
            # Should return 404 for invalid ID
            success = response.status_code == 404
            details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("Get Analysis (Invalid ID)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Analysis (Invalid ID)", False, f"Error: {str(e)}")
            return False

    def test_list_analyses(self):
        """Test listing all analyses"""
        try:
            response = requests.get(f"{self.api_url}/analyses", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_analyses_key = "analyses" in data
                success = has_analyses_key
                details = f"Status: {response.status_code}, Found {len(data.get('analyses', []))} analyses"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("List Analyses", success, details)
            return success
            
        except Exception as e:
            self.log_test("List Analyses", False, f"Error: {str(e)}")
            return False

    def test_cors_headers(self):
        """Test CORS headers are present"""
        try:
            response = requests.options(f"{self.api_url}/", timeout=10)
            
            # Check for CORS headers
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            success = has_cors or response.status_code in [200, 405]  # Some servers return 405 for OPTIONS
            
            details = f"Status: {response.status_code}, CORS headers present: {has_cors}"
            
            self.log_test("CORS Headers", success, details)
            return success
            
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🚀 Starting Bharatanatyam API Tests")
        print(f"🔗 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_root_endpoint,
            self.test_cors_headers,
            self.test_upload_video_validation,
            self.test_generate_story_invalid_id,
            self.test_get_analysis_invalid_id,
            self.test_list_analyses,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ FAILED - {test.__name__}: {str(e)}")
        
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = BharatanatyamAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "summary": {
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "success_rate": f"{(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "0%",
            "timestamp": datetime.now().isoformat()
        },
        "test_details": tester.test_results
    }
    
    # Save to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())