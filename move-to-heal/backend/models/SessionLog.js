const mongoose = require('mongoose');

const sessionLogSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    exerciseType: { type: String, required: true },
    date: { type: Date, default: Date.now },
    duration_seconds: { type: Number, required: true },
    reps_completed: { type: Number, required: true },
    form_accuracy_score: { type: Number },
    calories_burned: { type: Number },
    mistakes_logged: [{ type: String }]
}, { timestamps: true });

module.exports = mongoose.model('SessionLog', sessionLogSchema);
