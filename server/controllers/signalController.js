const Signal = require('../models/Signal');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Process an image through the ML model
exports.processImage = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No image uploaded' });
    }
    
    const imagePath = path.join(__dirname, '..', 'uploads', req.file.filename);
    console.log('Image path:', imagePath);
    
    const scriptPath = path.join(__dirname, '..', '..', 'machine_learning', 'scripts', 'predict.py');
    console.log('Script path:', scriptPath);
    
    // Check if files exist
    if (!fs.existsSync(imagePath)) {
      return res.status(404).json({ message: 'Uploaded image not found on server' });
    }
    
    if (!fs.existsSync(scriptPath)) {
      return res.status(404).json({ message: 'Python script not found' });
    }
    
    // Run the Python script with better error handling
    const python = spawn('python', [scriptPath, imagePath]);
    
    let dataString = '';
    let errorString = '';
    
    // Collect data from script
    python.stdout.on('data', (data) => {
      dataString += data.toString();
      console.log('Python output:', data.toString());
    });
    
    // Handle errors
    python.stderr.on('data', (data) => {
      errorString += data.toString();
      console.error(`Python Error: ${data}`);
    });
    
    // Handle process errors
    python.on('error', (error) => {
      console.error(`Failed to start Python process: ${error.message}`);
      return res.status(500).json({ 
        message: 'Failed to start Python process', 
        error: error.message 
      });
    });
    
    // When the script is done
    python.on('close', (code) => {
      console.log('Python process completed with code:', code);
      console.log('Raw output:', dataString);
      
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        return res.status(500).json({ 
          message: 'Error processing image', 
          error: errorString || `Process exited with code ${code}`
        });
      }
      
      try {
        // Find and extract the JSON part
        const jsonStart = dataString.indexOf('{');
        const jsonEnd = dataString.lastIndexOf('}') + 1;
        
        if (jsonStart < 0 || jsonEnd <= 0 || jsonStart >= jsonEnd) {
          throw new Error('No valid JSON found in the output');
        }
        
        const jsonString = dataString.substring(jsonStart, jsonEnd);
        console.log('Extracted JSON:', jsonString);
        
        const result = JSON.parse(jsonString);
        
        // Check if there was an error from Python
        if (result.error) {
          return res.status(500).json({ 
            message: 'Error in Python script', 
            error: result.error 
          });
        }
        
        // Provide meanings based on signal type
        let meaning = '';
        let suggestions = '';
        
        if (result.class === 'start_restart') {
          meaning = 'Signal to start or restart the game';
          suggestions = 'Clear and decisive hand motion';
        } else if (result.class === 'direction_pass') {
          meaning = 'Indicating direction or path of play';
          suggestions = 'More pronounced pointing gesture';
        } else if (result.class === 'timeout') {
          meaning = 'Timeout requested or granted';
          suggestions = 'Standard timeout signal';
        }
        
        res.json({
          imagePath: `/uploads/${req.file.filename}`,
          signalType: result.class,
          accuracy: result.confidence * 100,
          meaning,
          suggestions,
          predictions: result.all_probs
        });
      } catch (error) {
        console.error('Error parsing results:', error, 'Raw output:', dataString);
        res.status(500).json({ 
          message: 'Error parsing results', 
          error: error.message,
          rawOutput: dataString 
        });
      }
    });
  } catch (error) {
    console.error('Controller error:', error);
    res.status(500).json({ message: error.message });
  }
};

// Get all signals
exports.getSignals = async (req, res) => {
  try {
    const signals = await Signal.find().sort({ createdAt: -1 });
    res.json(signals);
  } catch (error) {
    console.error('Error getting signals:', error);
    res.status(500).json({ message: error.message });
  }
};

// Get a single signal
exports.getSignalById = async (req, res) => {
  try {
    const signal = await Signal.findById(req.params.id);
    if (!signal) {
      return res.status(404).json({ message: 'Signal not found' });
    }
    res.json(signal);
  } catch (error) {
    console.error('Error getting signal by ID:', error);
    res.status(500).json({ message: error.message });
  }
};

// Create a new signal entry
exports.createSignal = async (req, res) => {
  try {
    console.log('Received signal creation request');
    console.log('Request body:', req.body);
    console.log('Request file:', req.file);

    const { signalType, accuracy, meaning, suggestions } = req.body;
    
    if (!req.file) {
      console.error('No file uploaded');
      return res.status(400).json({ message: 'No image uploaded' });
    }
    
    const imagePath = `/uploads/${req.file.filename}`;
    
    const signal = new Signal({
      imagePath,
      signalType,
      accuracy: parseFloat(accuracy),
      meaning,
      suggestions
    });
    
    console.log('Creating signal:', signal);
    
    const savedSignal = await signal.save();
    
    console.log('Signal saved successfully:', savedSignal);
    
    res.status(201).json(savedSignal);
  } catch (error) {
    console.error('Detailed error in createSignal:', error);
    res.status(400).json({ 
      message: 'Error creating signal', 
      error: error.message,
      stack: error.stack 
    });
  }
};

// Delete a signal
exports.deleteSignal = async (req, res) => {
  try {
    const signal = await Signal.findById(req.params.id);
    if (!signal) {
      return res.status(404).json({ message: 'Signal not found' });
    }
    
    await Signal.deleteOne({ _id: req.params.id });
    res.json({ message: 'Signal removed' });
  } catch (error) {
    console.error('Error deleting signal:', error);
    res.status(500).json({ message: error.message });
  }
};