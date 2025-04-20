import express from 'express';
import multer from 'multer';  // Used for file uploads
import axios from 'axios';  // For making HTTP requests to Hugging Face
import fs from 'fs';
import dotenv from 'dotenv';  // For loading environment variables (like your API key)
import { fileURLToPath } from 'url';
import path from 'path';

dotenv.config();  // Load variables from .env file

const app = express();
const port = 3000;

// Get the current file's directory in an ES module environment
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Set up Multer to handle image uploads
const upload = multer({ dest: 'uploads/' });

// Hugging Face API URL and Model
const huggingFaceAPI = "https://api-inference.huggingface.co/models/Wvolf/ViT_Deepfake_Detection";

// POST route to handle image upload
app.post('/check-image', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No image uploaded');
  }

  // Read the uploaded image and convert it to base64
  const imagePath = path.join(__dirname, req.file.path);
  const imageBase64 = fs.readFileSync(imagePath, { encoding: 'base64' });

  try {
    // Call the Hugging Face model with Axios
    const response = await axios.post(huggingFaceAPI, {
      inputs: imageBase64,  // Send the base64 string as part of the request body
    }, {
      headers: {
        Authorization: `Bearer ${process.env.HUGGINGFACE_API_KEY}`,  // Using API Key from .env
        'Content-Type': 'application/json',
      }
    });
    

    // If the request is successful, return the response data
    res.json({ message: 'Image processed successfully', data: response.data });
  } catch (error) {
    console.error('Error processing image:', error);
    
    // Check if the error is related to authentication
    if (error.response && error.response.status === 401) {
      return res.status(401).send('Unauthorized - Invalid API Key');
    }

    // Generic error message
    res.status(500).send('Error processing the image');
  } finally {
    // Optionally delete the uploaded file
    try {
      fs.unlinkSync(imagePath);  // Clean up the uploaded file
    } catch (cleanupError) {
      console.error('Error deleting uploaded file:', cleanupError);
    }
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://127.0.0.1:${port}`);
});
