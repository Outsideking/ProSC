require('dotenv').config();
const axios = require('axios');
const mongoose = require('mongoose');
const fs = require('fs');
const PDFDocument = require('pdfkit');

// ==========================
// CONFIG
// ==========================
const PROSC_API_KEY = process.env.PROSC_API_KEY;
const BASE_URL = "https://api.prosc.io/v1";
const HEADERS = { Authorization: `Bearer ${PROSC_API_KEY}`, "Content-Type": "application/json" };
const MONGO_URI = process.env.MONGO_URI;
const TARGET_URL = process.env.TARGET_URL;

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const OTHER_AI_API_KEY = process.env.OTHER_AI_API_KEY;

const WHATSAPP_API_URL = process.env.WHATSAPP_API_URL;
const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;

// ==========================
// MONGODB SCHEMA
// ==========================
const ResultSchema = new mongoose.Schema({
  scanId: { type: String, unique: true },
  target: String,
  timestamp: { type: Date, default: Date.now },
  vulnerabilities: mongoose.Schema.Types.Mixed,
  status: String,
  pdfFile: String
});
const ScanResult = mongoose.model('ScanResult', ResultSchema);

// ==========================
// ProSC API Functions
// ==========================
async function startScan(target, metadata){
  const payload = { target, scan_type: "full", filters:["html","api","assets"], metadata };
  const resp = await axios.post(`${BASE_URL}/scan`, payload, { headers: HEADERS });
  return resp.data;
}

async function checkScanStatus(scanId){
  const resp = await axios.get(`${BASE_URL}/scan/status/${scanId}`, { headers: HEADERS });
  return resp.data;
}

async function getResults(scanId){
  const resp = await axios.get(`${BASE_URL}/results`, { headers: HEADERS, params: { scan_id: scanId } });
  return resp.data;
}

// ==========================
// DB Functions
// ==========================
async function connectDB(){
  await mongoose.connect(MONGO_URI);
  console.log("MongoDB connected");
}

async function saveResults(scanId,target,status,results,pdfFile){
  const scan = new ScanResult({ scanId, target, status, vulnerabilities: results, pdfFile });
  await scan.save();
  console.log(`Scan results saved: ${scanId}`);
}

// ==========================
// AI Data Fetching
// ==========================
async function fetchOpenAIInsights(target){
  try{
    const resp = await axios.post('https://api.openai.com/v1/chat/completions',{
      model:"gpt-4",
      messages:[
        {role:"system", content:"Analyze security aspects of target URL"}, 
        {role:"user", content:`Provide potential vulnerabilities and metadata for ${target}`}
      ]
    },{
      headers: { Authorization: `Bearer ${OPENAI_API_KEY}` }
    });
    return resp.data.choices[0].message.content;
  } catch(err){
    console.error("OpenAI fetch error:", err.message);
    return null;
  }
}

async function fetchOtherAIInsights(target){
  // ตัวอย่าง Template สำหรับ AI อื่น
  try{
    const resp = await axios.get(`https://api.other-ai.com/scan?target=${target}`,{
      headers:{ Authorization:`Bearer ${OTHER_AI_API_KEY}` }
    });
    return resp.data;
  } catch(err){
    console.error("Other AI fetch error:", err.message);
    return null;
  }
}

// ==========================
// PDF Report
// ==========================
function createPDF(scan){
  const doc = new PDFDocument();
  const fileName = `scan_report_${scan.scanId}.pdf`;
  doc.pipe(fs.createWriteStream(fileName));

  doc.fontSize(20).text(`Scan Report: ${scan.target}`, { underline:true });
  doc.moveDown();
  doc.fontSize(12).text(`Scan ID: ${scan.scanId}`);
  doc.text(`Status: ${scan.status}`);
  doc.text(`Timestamp: ${scan.timestamp}`);
  doc.moveDown();

  if(scan.vulnerabilities?.details){
    scan.vulnerabilities.details.forEach(v=>{
      doc.text(`Type: ${v.type || 'Unknown'}`);
      doc.text(`Severity: ${v.severity || 'Low'}`);
      doc.text(`Description: ${v.description || '-'}`);
      doc.moveDown();
    });
  } else {
    doc.text("No vulnerabilities found.");
  }

  doc.end();
  return fileName;
}

// ==========================
// WhatsApp Notification
// ==========================
async function sendWhatsApp(fileName, scan){
  try{
    await axios.post(WHATSAPP_API_URL, {
      to: 'RECIPIENT_NUMBER',
      message: `Scan Completed: ${scan.target}\nScan ID: ${scan.scanId}`,
      attachment: fileName
    }, { headers: { Authorization: `Bearer ${WHATSAPP_TOKEN}` } });
    console.log("WhatsApp notification sent");
  } catch(err){
    console.error("WhatsApp send error:", err.message);
  }
}

// ==========================
// Pipeline
// ==========================
async function runPipeline(){
  try{
    await connectDB();

    console.log(`Fetching AI insights for ${TARGET_URL}...`);
    const openAIData = await fetchOpenAIInsights(TARGET_URL);
    const otherAIData = await fetchOtherAIInsights(TARGET_URL);

    const combinedMetadata = { openAI: openAIData, otherAI: otherAIData };

    console.log(`Starting ProSC scan for ${TARGET_URL} with AI metadata...`);
    const scanResp = await startScan(TARGET_URL, combinedMetadata);
    const scanId = scanResp.scan_id;

    // ตรวจสอบสถานะจนเสร็จ
    let status;
    do{
      status = await checkScanStatus(scanId);
      console.log(`Scan status: ${status.status}`);
      if(status.status !== 'completed') await new Promise(r=>setTimeout(r,5000));
    } while(status.status !== 'completed');

    // ดึงผลลัพธ์
    const results = await getResults(scanId);

    // สร้าง PDF
    const scanObj = { scanId, target: TARGET_URL, status: status.status, timestamp: new Date(), vulnerabilities: results };
    const pdfFile = createPDF(scanObj);

    // บันทึกลง MongoDB
    await saveResults(scanId, TARGET_URL, status.status, results, pdfFile);

    // ส่ง WhatsApp
    await sendWhatsApp(pdfFile, scanObj);

    console.log("Full Auto Pipeline finished successfully!");
  } catch(err){
    console.error("Pipeline error:", err.message);
  } finally{
    mongoose.connection.close();
  }
}

// ==========================
// Auto-run
// ==========================
runPipeline();
// สามารถตั้ง Scheduler เช่น cron หรือ setInterval เพื่อรันทุกวัน/ทุกชั่วโมง
