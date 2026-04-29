const express = require('express');
const Profile = require('../models/Profile');
const router = express.Router();

router.post('/generate', async (req, res) => {
    try {
        const { userId, bmr, tdee, goal } = req.body;

        let target_calories = tdee;
        if (goal === 'weight_loss') target_calories -= 500;
        if (goal === 'weight_gain') target_calories += 500;

        // MVP: Serve static diet plans matching caloric needs
        const meal_plan = {
            target_calories,
            meals: {
                breakfast: "Oats & Fruits (300 kcal)",
                lunch: "2 Roti, Dal, Sabzi (500 kcal)",
                snack: "Roasted Chana (150 kcal)",
                dinner: "Paneer Salad / Grilled Chicken (400 kcal)"
            }
        };

        res.json({ message: "Diet generated successfully", meal_plan });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
