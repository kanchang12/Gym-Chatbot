const express = require('express');
const cors = require('cors');
const axios = require('axios');
const FormData = require('form-data');

const app = express();
app.use(cors());
app.use(express.json());

app.post('/submit-to-zoho', async (req, res) => {
    try {
        const formData = new FormData();
        formData.append('First Name', req.body.firstName);
        formData.append('Last Name', req.body.lastName);
        formData.append('Email', req.body.email);
        formData.append('Message', req.body.message);

        const response = await axios.post(
            'https://forms.zohopublic.in/banglaygolpo1/form/ContactUs/formperma/tygGH6LFquRO7lGxeTjGLt7WjgEioGLQf2F6L6XKSPo',
            formData,
            { headers: formData.getHeaders() }
        );

        res.json({ success: true, message: 'Form submitted successfully!' });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Submission failed', error: error.message });
    }
});

app.listen(3001, () => console.log('Server running on port 3001'));
