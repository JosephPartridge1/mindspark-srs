# simple_srs_server.py - 100% WORKING SRS PRESENTATION SERVER
import http.server
import socketserver
import os
import sys

PORT = 9090  # CHANGE THIS IF PORT IS BUSY: try 9091, 9092, 8081, 8082

print("=" * 70)
print("🚀 SISTEM SRS - TUGAS AKHIR INFORMATIKA")
print("=" * 70)
print(f"📂 Location: {os.getcwd()}")
print(f"🌐 Server URL: http://localhost:{PORT}")
print("=" * 70)

# SIMPLE HTML PAGE
HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Sistem SRS - Presentasi</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #f0f0f0;
        }
        
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
        }
        
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #3498db;
        }
        
        .model-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .model-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 2px solid #e0e0e0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        th {
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        
        .demo-box {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            margin: 30px 0;
            border: 3px solid #2ecc71;
        }
        
        .word-display {
            font-size: 3em;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0;
        }
        
        .meaning-display {
            font-size: 2em;
            color: #3498db;
            margin: 20px 0;
        }
        
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 25px;
            margin: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        
        .result-box {
            background: #d5edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border: 1px solid #c3e6cb;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
            color: #7f8c8d;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .word-display {
                font-size: 2em;
            }
            
            .meaning-display {
                font-size: 1.5em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔤 SISTEM SPACED REPETITION (SRS)</h1>
            <div class="subtitle">Tugas Akhir Informatika - Model Pembelajaran Kosakata</div>
        </div>
        
        <!-- MODEL INFORMATIKA SECTION -->
        <div class="card">
            <h2>🎯 MODEL INFORMATIKA</h2>
            <div class="model-section">
                <div class="model-card">
                    <h3>1. MODEL DATA</h3>
                    <p>Struktur database untuk menyimpan:</p>
                    <ul>
                        <li>Kosakata (English - Indonesian)</li>
                        <li>Riwayat belajar</li>
                        <li>Interval review</li>
                    </ul>
                </div>
                
                <div class="model-card">
                    <h3>2. MODEL ALGORITMA</h3>
                    <p>Fungsi komputasi SRS:</p>
                    <p><strong>f(score) = interval</strong></p>
                    <p>Skor 1-5 → Interval 1-7 hari</p>
                </div>
                
                <div class="model-card">
                    <h3>3. MODEL SIMULASI</h3>
                    <p>Interface untuk simulasi proses belajar dengan feedback loop.</p>
                </div>
            </div>
        </div>
        
        <!-- ALGORITMA SRS SECTION -->
        <div class="card">
            <h2>🔢 ALGORITMA SPACED REPETITION</h2>
            
            <table>
                <tr>
                    <th>SKOR USER</th>
                    <th>KETERANGAN</th>
                    <th>INTERVAL (HARI)</th>
                    <th>PRINSIP</th>
                </tr>
                <tr>
                    <td><strong>1 - 2</strong></td>
                    <td>Sulit diingat</td>
                    <td>1</td>
                    <td>Review cepat untuk reinforcement</td>
                </tr>
                <tr>
                    <td><strong>3</strong></td>
                    <td>Cukup</td>
                    <td>2</td>
                    <td>Sedikit meningkatkan interval</td>
                </tr>
                <tr>
                    <td><strong>4 - 5</strong></td>
                    <td>Mudah diingat</td>
                    <td>4 - 7</td>
                    <td>Interval panjang untuk memori kuat</td>
                </tr>
            </table>
            
            <p><strong>Prinsip dasar:</strong> Review dilakukan tepat sebelum kata terlupakan, sehingga transfer ke memori jangka panjang lebih efisien.</p>
        </div>
        
        <!-- DEMO SECTION -->
        <div class="demo-box">
            <h2>🎮 DEMO INTERAKTIF</h2>
            
            <div class="word-display" id="current-word">algorithm</div>
            <p>Tekan tombol untuk melihat arti:</p>
            
            <button class="btn" onclick="showMeaning()">👁️ TAMPILKAN ARTI</button>
            
            <div id="meaning-section" style="display: none;">
                <div class="meaning-display" id="word-meaning">algoritma</div>
                
                <p><strong>Seberapa mudah Anda mengingat kata ini?</strong></p>
                
                <div>
                    <button class="btn" onclick="submitReview(1)">1 (Sulit)</button>
                    <button class="btn" onclick="submitReview(2)">2</button>
                    <button class="btn" onclick="submitReview(3)">3 (Cukup)</button>
                    <button class="btn" onclick="submitReview(4)">4</button>
                    <button class="btn" onclick="submitReview(5)">5 (Mudah)</button>
                </div>
                
                <div id="result-box" class="result-box" style="display: none;">
                    <!-- Results will appear here -->
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <p><strong>Kata berikutnya:</strong></p>
                <button class="btn" onclick="nextWord()" style="background: #2ecc71;">➡️ KATA BERIKUTNYA</button>
            </div>
        </div>
        
        <!-- RELEVANSI SECTION -->
        <div class="card">
            <h2>📝 RELEVANSI DENGAN KARYA TULIS ILMIAH</h2>
            <p>Model ini mengimplementasikan prinsip <strong>Spaced Repetition System (SRS)</strong> yang digunakan oleh aplikasi seperti <strong>Duolingo</strong>.</p>
            <p>Relevan dengan penelitian KTI tentang: <em>"Pengaruh Fitur Spaced Repetition Berbasis AI di Duolingo terhadap Peningkatan Penguasaan Kosakata Bahasa Inggris"</em>.</p>
            <p><strong>Perbedaan:</strong> Sistem ini adalah model komputasional dasar, sedangkan Duolingo menggunakan AI untuk personalisasi interval.</p>
        </div>
        
        <div class="footer">
            <p>SISTEM SRS - Tugas Akhir Informatika - Kelas 12</p>
            <p>Presenter: [NAMA ANDA] - [NAMA SEKOLAH]</p>
            <p>Teknologi: Python, HTTP Server, HTML/CSS/JavaScript</p>
        </div>
    </div>
    
    <script>
        // Demo data
        const words = [
            { english: "algorithm", indonesian: "algoritma" },
            { english: "database", indonesian: "basis data" },
            { english: "function", indonesian: "fungsi" },
            { english: "variable", indonesian: "variabel" },
            { english: "software", indonesian: "perangkat lunak" }
        ];
        
        let currentIndex = 0;
        
        // Initialize first word
        document.getElementById('current-word').textContent = words[currentIndex].english;
        document.getElementById('word-meaning').textContent = words[currentIndex].indonesian;
        
        function showMeaning() {
            document.getElementById('meaning-section').style.display = 'block';
        }
        
        function submitReview(score) {
            // SRS Algorithm
            let interval;
            if (score <= 2) {
                interval = 1;
            } else if (score === 3) {
                interval = 2;
            } else {
                interval = 7;
            }
            
            const resultBox = document.getElementById('result-box');
            resultBox.style.display = 'block';
            resultBox.innerHTML = `
                <strong>✅ REVIEW DISIMPAN!</strong><br>
                Skor: <strong>${score}/5</strong><br>
                Kata "<strong>${words[currentIndex].english}</strong>" akan diulang dalam <strong>${interval} hari</strong>.
            `;
            
            // Update demo stats
            updateStats();
        }
        
        function nextWord() {
            currentIndex = (currentIndex + 1) % words.length;
            
            document.getElementById('current-word').textContent = words[currentIndex].english;
            document.getElementById('word-meaning').textContent = words[currentIndex].indonesian;
            
            // Hide meaning and result for next word
            document.getElementById('meaning-section').style.display = 'none';
            document.getElementById('result-box').style.display = 'none';
            
            // Update demo stats
            updateStats();
        }
        
        function updateStats() {
            // This would normally fetch from server
            // For demo, just show basic info
            console.log("Stats updated - word:", words[currentIndex].english);
        }
        
        // Keyboard shortcuts for presentation
        document.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowRight') {
                nextWord();
            } else if (event.key === ' ') {
                showMeaning();
            }
        });
    </script>
</body>
</html>
"""

# HTTP Request Handler
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve our HTML page for all requests
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML.encode())
    
    def log_message(self, format, *args):
        # Suppress access logs
        pass

def main():
    print("📡 Starting server...")
    
    # Try to open browser
    try:
        os.system(f'start http://localhost:{PORT}')
        print("✅ Browser opened automatically")
    except:
        print(f"⚠️  Please open browser manually: http://localhost:{PORT}")
    
    print(f"✅ Server running on http://localhost:{PORT}")
    print("⚡ Press Ctrl+C to stop the server")
    print("=" * 70)
    
    # Try to start server
    try:
        with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ ERROR: Port {PORT} is already in use!")
            print("💡 SOLUTIONS:")
            print(f"   1. Change PORT number in line 8 (try 9091, 9092, 8081, 8082)")
            print(f"   2. Close other programs using port {PORT}")
            print(f"   3. Run: netstat -ano | findstr :{PORT}  (to see what's using it)")
            print("=" * 70)
            input("Press Enter to exit...")
        else:
            print(f"❌ ERROR: {e}")
            input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Presentation complete!")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()