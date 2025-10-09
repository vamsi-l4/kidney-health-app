import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

async function testServer() {
  console.log('🧪 Testing Node.js Server...\n');

  try {
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const healthResponse = await axios.get(`${BASE_URL}/health`);
    console.log('✅ Health:', healthResponse.data);

    // Test welcome endpoint
    console.log('\n2. Testing welcome endpoint...');
    const welcomeResponse = await axios.get(`${BASE_URL}/welcome`);
    console.log('✅ Welcome:', welcomeResponse.data);

    // Test user registration
    console.log('\n3. Testing user registration...');
    const registerResponse = await axios.post(`${BASE_URL}/api/register`, {
      email: 'test@example.com',
      password: 'testpass123',
      name: 'Test User'
    });
    console.log('✅ Register:', registerResponse.data);

    // Test user login
    console.log('\n4. Testing user login...');
    const loginResponse = await axios.post(`${BASE_URL}/api/login`, {
      email: 'test@example.com',
      password: 'testpass123'
    });
    console.log('✅ Login:', loginResponse.data);

    const token = loginResponse.data.access_token;

    // Test authenticated endpoints
    console.log('\n5. Testing authenticated endpoints...');
    const reportsResponse = await axios.get(`${BASE_URL}/api/reports`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('✅ Reports:', reportsResponse.data);

    // Test forgot password
    console.log('\n6. Testing forgot password...');
    const forgotResponse = await axios.post(`${BASE_URL}/api/forgot-password`, {
      email: 'test@example.com'
    });
    console.log('✅ Forgot Password:', forgotResponse.data);

    console.log('\n🎉 All tests passed! Server is working correctly.');
    process.exit(0);

  } catch (error) {
    console.error('\n❌ Test failed:', error.response?.data || error.message);
    console.log('\n💡 Make sure the server is running with: npm start');
    process.exit(1);
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testServer();
}

export default testServer;
