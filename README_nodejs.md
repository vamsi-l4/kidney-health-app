# Kidney Stone Predictor - Node.js Server

This is the Node.js/Express equivalent of the Python FastAPI server for the Kidney Stone Predictor application.

## Features

- **Authentication**: JWT-based authentication with login, register, forgot password, OTP verification, and password reset
- **File Upload**: Image upload with validation and processing
- **Prediction**: Placeholder for ML model prediction (ready for PyTorch model integration)
- **Report Management**: CRUD operations for user reports
- **CORS Support**: Configured for cross-origin requests
- **Error Handling**: Comprehensive error handling and logging

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration
- `POST /api/forgot-password` - Request password reset
- `POST /api/verify-otp` - Verify OTP for password reset
- `POST /api/reset-password` - Reset user password

### Prediction
- `POST /api/predict` - Upload image for kidney stone prediction

### Reports
- `GET /api/reports` - Get user reports (requires authentication)
- `POST /api/reports` - Add new report (requires authentication)
- `DELETE /api/reports/:report_id` - Delete report (requires authentication)

### Health & Info
- `GET /health` - Health check
- `GET /welcome` - Welcome message with request logging

## Key Differences from Python FastAPI Version

### 1. **Language & Framework**
- **Python FastAPI** → **Node.js/Express**
- Async/await support in both versions

### 2. **Authentication**
- **Python**: Uses `python-jose` for JWT
- **Node.js**: Uses `jsonwebtoken` library
- Password hashing: `bcryptjs` instead of Python's bcrypt

### 3. **File Handling**
- **Python**: Uses FastAPI's `UploadFile`
- **Node.js**: Uses `multer` for multipart file uploads
- Files stored in `server/app/uploads/` directory

### 4. **Data Storage**
- Both versions use JSON files for user and report storage
- **Python**: `users.json`, `user_reports.json`
- **Node.js**: Same file structure maintained

### 5. **ML Model Integration**
- **Python**: Direct PyTorch model loading and inference
- **Node.js**: Placeholder function `simulatePrediction()` - ready for model integration
- To integrate actual model: Replace `simulatePrediction()` with actual PyTorch model loading

### 6. **Middleware**
- **Python**: FastAPI middleware for CORS
- **Node.js**: Express middleware for CORS and authentication

### 7. **Error Handling**
- **Python**: FastAPI's automatic error handling
- **Node.js**: Manual error handling with custom middleware

## Environment Variables

```env
PORT=8000
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## Migration Notes

1. **Data Compatibility**: User and report data stored in JSON files is compatible between versions
2. **API Compatibility**: All endpoints maintain the same structure and response format
3. **Authentication**: JWT tokens from Python version may not work due to different signing libraries
4. **Model Integration**: The Node.js version has a placeholder for ML model - you'll need to integrate your PyTorch model

## Development

The server includes:
- ES6 modules (import/export)
- Modern async/await patterns
- Comprehensive error handling
- Request logging
- File upload validation
- JWT token validation middleware

## Production Considerations

1. Replace `simulatePrediction()` with actual model inference
2. Configure proper CORS origins
3. Use environment variables for sensitive data
4. Consider using a database instead of JSON files
5. Add rate limiting and security headers
6. Use Redis for OTP storage instead of in-memory Map
