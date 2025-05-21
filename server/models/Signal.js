const mongoose = require('mongoose');

const SignalSchema = new mongoose.Schema({
  imagePath: {
    type: String,
    required: true
  },
  signalType: {
    type: String,
    enum: ['start_restart', 'direction_pass', 'timeout'],
    required: true
  },
  accuracy: {
    type: Number,
    required: true
  },
  meaning: {
    type: String,
    required: true
  },
  suggestions: {
    type: String,
    default: ''
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Signal', SignalSchema);