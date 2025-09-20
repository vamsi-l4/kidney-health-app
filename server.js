import express from 'express';
import cors from 'cors';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors({
  origin: "*", // Change in production
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'app', 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = uuidv4() + path.extname(file.originalname);
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

// Configuration
const SECRET_KEY = process.env.SECRET_KEY || "change-me-please";
const ALGORITHM = process.env.ALGORITHM || "HS256";
const ACCESS_TOKEN_EXPIRE_MINUTES = parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES || "120");

const USERS_FILE = path.join(__dirname, 'app', 'users.json');
const REPORTS_FILE = path.join(__dirname, 'app', 'user_reports.json');

// Ensure data files exist
if (!fs.existsSync(USERS_FILE)) {
  fs.writeFileSync(USERS_FILE, JSON.stringify({}));
}

if (!fs.existsSync(REPORTS_FILE)) {
  fs.writeFileSync(REPORTS_FILE, JSON.stringify({}));
}

// OTP store (in production, use Redis or database)
const otpStore = new Map();

// Utility functions
function createAccessToken(data, expiresIn = ACCESS_TOKEN_EXPIRE_MINUTES * 60) {
  return jwt.sign(data, SECRET_KEY, { expiresIn });
}

function verifyToken(token) {
  try {
    return jwt.verify(token, SECRET_KEY);
  } catch (error) {
    throw new Error('Invalid token');
  }
}

// Authentication middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ detail: 'Access token required' });
  }

  try {
    const decoded = verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ detail: 'Invalid token' });
  }
}

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Welcome endpoint with logging
app.get('/welcome', (req, res) => {
  console.log(`Request received: ${req.method} ${req.path}`);
  res.json({ message: 'Welcome to the Kidney Stone Predictor API!' });
});

// Authentication routes
app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

    if (users[email] && await bcrypt.compare(password, users[email].password)) {
      const token = createAccessToken({ sub: email });
      const { password: _, ...userWithoutPassword } = users[email];
      res.json({
        access_token: token,
        token_type: 'bearer',
        user: userWithoutPassword
      });
    } else {
      res.status(401).json({ detail: 'Invalid credentials' });
    }
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.post('/api/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

    if (users[email]) {
      return res.status(400).json({ detail: 'User already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    users[email] = {
      password: hashedPassword,
      name: name
    };

    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));

    const token = createAccessToken({ sub: email });
    const { password: _, ...userWithoutPassword } = users[email];

    res.json({
      access_token: token,
      token_type: 'bearer',
      user: userWithoutPassword
    });
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.post('/api/forgot-password', (req, res) => {
  try {
    const { email } = req.body;

    const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

    if (!users[email]) {
      return res.status(400).json({ detail: 'User not found' });
    }

    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    otpStore.set(email, otp);

    // In real app, send email with OTP
    console.log(`OTP for ${email}: ${otp}`); // For testing

    res.json({ message: 'OTP sent to email' });
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.post('/api/verify-otp', (req, res) => {
  try {
    const { email, otp } = req.body;

    if (otpStore.get(email) === otp) {
      otpStore.delete(email);
      res.json({ message: 'OTP verified' });
    } else {
      res.status(400).json({ detail: 'Invalid OTP' });
    }
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.post('/api/reset-password', async (req, res) => {
  try {
    const { email, new_password } = req.body;

    const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

    if (!users[email]) {
      return res.status(400).json({ detail: 'User not found' });
    }

    const hashedPassword = await bcrypt.hash(new_password, 10);
    users[email].password = hashedPassword;

    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));

    res.json({ message: 'Password reset successful' });
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

// Prediction endpoint
app.post('/api/predict', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ detail: 'No file uploaded' });
    }

    // Placeholder for ML model prediction
    // In a real implementation, you would load your PyTorch model here
    // For now, we'll simulate a prediction
    const prediction = await simulatePrediction(req.file);

    res.json({
      filename: req.file.filename,
      prediction: prediction
    });
  } catch (error) {
    console.error('Prediction error:', error);
    res.status(500).json({ detail: error.message || 'Prediction failed' });
  }
});

// Simulate ML prediction (replace with actual model loading)
async function simulatePrediction(file) {
  // This is a placeholder - replace with actual model inference
  // You would need to load your PyTorch model and run inference here

  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Simulate random prediction (replace with actual model)
  const isStone = Math.random() > 0.5;
  const confidence = 0.7 + Math.random() * 0.3; // 0.7 to 1.0

  return {
    label: isStone ? "stone" : "non-stone",
    confidence: Math.round(confidence * 10000) / 10000
  };
}

// Reports endpoints
app.get('/api/reports', authenticateToken, (req, res) => {
  try {
    const email = req.user.sub;
    const reports = JSON.parse(fs.readFileSync(REPORTS_FILE, 'utf8'));
    const userReports = reports[email] || [];
    res.json(userReports);
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.post('/api/reports', authenticateToken, (req, res) => {
  try {
    const email = req.user.sub;
    const { name, prediction, createdAt } = req.body;

    const reports = JSON.parse(fs.readFileSync(REPORTS_FILE, 'utf8'));

    if (!reports[email]) {
      reports[email] = [];
    }

    const reportData = {
      id: uuidv4(),
      name,
      prediction,
      createdAt
    };

    reports[email].push(reportData);
    fs.writeFileSync(REPORTS_FILE, JSON.stringify(reports, null, 2));

    res.json({ message: 'Report added' });
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.delete('/api/reports/:report_id', authenticateToken, (req, res) => {
  try {
    const email = req.user.sub;
    const { report_id } = req.params;

    const reports = JSON.parse(fs.readFileSync(REPORTS_FILE, 'utf8'));

    if (reports[email]) {
      reports[email] = reports[email].filter(report => report.id !== report_id);
      fs.writeFileSync(REPORTS_FILE, JSON.stringify(reports, null, 2));
    }

    res.json({ message: 'Report deleted' });
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Error:', error);
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ detail: 'File too large' });
    }
  }
  res.status(500).json({ detail: error.message || 'Internal server error' });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ detail: 'Endpoint not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🎉 Welcome: http://localhost:${PORT}/welcome`);
});

export default app;
