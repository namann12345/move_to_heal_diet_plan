const mongoose = require('mongoose');

const profileSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    goal: { type: String, enum: ['weight_loss', 'weight_gain', 'maintenance', 'rehab'], required: true },
    age: { type: Number, required: true },
    height_cm: { type: Number, required: true },
    weight_kg: { type: Number, required: true },
    gender: { type: String, enum: ['male', 'female', 'other'], required: true },
    activity_level: { type: String, enum: ['sedentary', 'moderate', 'active'], required: true },
    diet_pref: { type: String, enum: ['veg', 'non-veg'], required: true },
    bmi: { type: Number },
    tdee: { type: Number },
    target_calories: { type: Number }
}, { timestamps: true });

module.exports = mongoose.model('Profile', profileSchema);
