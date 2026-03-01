# 🛰️ Aura Trade AI - Sistema de Monitoreo Pro
<p align="center">
  <img src="logo.png" width="250">
</p>

![GitHub Actions](https://img.shields.io/badge/Status-Active-success?style=for-the-badge&logo=githubactions)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Aura Trade AI** es un bot de análisis técnico automatizado que utiliza Inteligencia Artificial para vigilar el mercado de criptomonedas las 24 horas del día.

## 🚀 Características Principales
* **🧠 Análisis con IA:** Utiliza modelos de Random Forest para predecir movimientos de precio en temporalidades de 1h.
* **📊 Multimoneda:** Vigilancia activa de **BTC, BNB, XRP y LTC**.
* **🚨 Modo Emergencia:** Alertas automáticas a Telegram si una moneda cae más de un 5% en una hora.
* **🌙 Modo Nocturno:** Reportes de rutina silenciados durante la madrugada (solo recibes alertas críticas).
* **💰 Cálculo de Rendimiento:** Resumen diario del rendimiento porcentual del portafolio.

## 🛠️ Tecnologías Usadas
- **CCXT:** Para la conexión directa con Binance.
- **Pandas TA:** Para el cálculo de indicadores técnicos (RSI, EMA).
- **Scikit-Learn:** Para el motor de Inteligencia Artificial.
- **GitHub Actions:** Para la ejecución automática cada 60 minutos.

## 📬 Notificaciones
El bot envía señales en tiempo real directamente a un canal privado de **Telegram**, incluyendo:
1. Señales de Compra 🚀
2. Reportes de Actividad cada hora ✅
3. Alertas de Caídas Críticas ⚠️

---
*Descargo de responsabilidad: Este software es para fines educativos. El trading de criptomonedas implica un alto riesgo.*

