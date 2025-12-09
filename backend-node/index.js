const express = require('express');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

// Configuración de Multer para recibir archivos en memoria 
const upload = multer({ storage: multer.memoryStorage() });

// --- MOCK---
const VALID_USERS = [
    { id: "123456", name: "PEPITO PEREZ", allowed: true },
    { id: "888888", name: "JUAN DEL PUEBLO", allowed: true }
];

app.use(express.json());

// Endpoint de prueba
app.get('/', (req, res) => {
    console.log("==> Ping recibido en backend-node");
    res.send({ status: "Backend Node.js Online", ai_service: process.env.AI_ENGINE_URL });
});

// Endpoint de autenticación
app.post('/auth', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No se envió ninguna imagen" });
        }

        console.log("--> Recibida solicitud de autenticación...");

        const form = new FormData();
        form.append('file', req.file.buffer, { filename: 'upload.jpg' });
        
        const AI_URL = process.env.AI_ENGINE_URL || 'http://engine-python:8000';
        
        // 1. Consultar OCR
        console.log(`--> Consultando OCR a ${AI_URL}...`);
        const ocrResponse = await axios.post(`${AI_URL}/analyze?type=document`, form, {
            headers: { ...form.getHeaders() }
        });
        
        const textFound = ocrResponse.data.raw_text || "";
        const textUpper = textFound.toUpperCase();
        console.log("--> Texto detectado:", textUpper);

        // Validar contra Mock DB
        const userMatch = VALID_USERS.find(user => textUpper.includes(user.name) || textUpper.includes(user.id));

        if (!userMatch) {
            console.log("--> RECHAZADO: Usuario no encontrado en BD.");
            return res.status(401).json({
                authorized: false,
                reason: "Documento no coincide con usuarios registrados",
                ocr_debug: textFound
            });
        }

        // 2. Consultar Liveness
        const form2 = new FormData();
        form2.append('file', req.file.buffer, { filename: 'face.jpg' });

        const livenessResponse = await axios.post(`${AI_URL}/analyze?type=face`, form2, {
            headers: { ...form2.getHeaders() }
        });

        const liveness = livenessResponse.data.liveness;
        
        // validar rostro ojos abiertos
        if (!liveness || !liveness.detected) {
             return res.status(401).json({
                authorized: false,
                reason: "No se detectó un rostro humano válido",
                details: liveness
            });
        }

        console.log(`--> APROBADO: Bienvenido ${userMatch.name}`);
        return res.json({
            authorized: true,
            user: userMatch,
            security_check: {
                ocr_match: true,
                liveness_passed: true,
                blink_data: liveness
            }
        });

    } catch (error) {
        console.error("Error en orquestación:", error.message);
        res.status(500).json({ error: "Error interno procesando la solicitud IA", details: error.message });
    }
});

app.listen(port, () => {
    console.log(`Orquestador Node.js escuchando en puerto ${port}`);
});